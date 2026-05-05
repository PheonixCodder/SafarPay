"""Identity Verification Engine for KYC."""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import cv2
import numpy as np
from deepface import DeepFace
from rapidfuzz import fuzz
from sp.core.observability.metrics import MetricsCollector
from verification.domain.exceptions import MLProcessingError
from verification.domain.models import DocumentType

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger("verification.engine")

MAX_IMAGE_SIZE_MB = 5
FACE_MATCH_THRESHOLD = 0.6
NAME_FUZZY_THRESHOLD = 85.0


@dataclass
class VerificationBundle:
    id_front: bytes
    id_back: bytes
    license_front: bytes
    license_back: bytes
    selfie: bytes

    id_front_meta: dict[str, Any] = field(default_factory=dict)
    license_front_meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    success: bool
    errors: list[dict[str, Any]]
    extracted_data: dict[str, Any]


class IdentityVerificationEngine:
    """Singleton engine for processing KYC ml workloads."""

    def __init__(self, metrics_collector: MetricsCollector | None = None) -> None:
        logger.info("Initializing ML Models...")
        self.metrics = metrics_collector
        if PaddleOCR:
            self.ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=False, show_log=False)
        else:
            self.ocr = None
        self.semaphore = asyncio.Semaphore(2)
        logger.info("ML Models loaded.")

    async def run(self, bundle: VerificationBundle) -> VerificationResult:
        """Asynchronous wrapper to enforce semaphore before hitting thread pool."""
        start_time = asyncio.get_event_loop().time()
        async with self.semaphore:
            try:
                result = await asyncio.get_event_loop().run_in_executor(None, self._run_internal, bundle)
            except Exception:
                if self.metrics:
                    duration = asyncio.get_event_loop().time() - start_time
                    self.metrics.histogram("identity_verification_duration", duration)
                    self.metrics.increment(
                        "identity_verification_total",
                        labels={"status": "failure"},
                    )
                raise

            if self.metrics:
                duration = asyncio.get_event_loop().time() - start_time
                self.metrics.histogram("identity_verification_duration", duration)
                self.metrics.increment(
                    "identity_verification_total",
                    labels={"status": "success" if result.success else "failure"},
                )
            return result

    def _run_internal(self, bundle: VerificationBundle) -> VerificationResult:
        """Synchronous method to run the entire verification pipeline."""
        errors = []
        extracted = {}

        try:
            # 1. Image Size Checks
            self._check_sizes(bundle)

            # 2. OCR Extraction
            cnic_text = self._extract_ocr(bundle.id_front, bundle.id_front_meta)
            license_text = self._extract_ocr(bundle.license_front, bundle.license_front_meta)

            # Store in extracted data for persistence
            extracted["cnic_raw_text"] = cnic_text
            extracted["license_raw_text"] = license_text

            # 3. Name Extraction & Matching
            cnic_extracted_name = self._extract_name_from_ocr(cnic_text)
            license_extracted_name = self._extract_name_from_ocr(license_text)

            cnic_name = self._normalize_name(cnic_extracted_name)
            license_name = self._normalize_name(license_extracted_name)

            if not self._cross_check_names(cnic_name, license_name):
                errors.append({
                    "code": "NAME_MISMATCH",
                    "details": f"Names do not match >= {NAME_FUZZY_THRESHOLD}%",
                    "document_type": DocumentType.ID_FRONT
                })

            # 4. Expiry Checks
            cnic_expiry = self._parse_date(cnic_text)
            license_expiry = self._parse_date(license_text)
            if not cnic_expiry or cnic_expiry < date.today():
                errors.append({
                    "code": "CNIC_EXPIRED_OR_INVALID",
                    "details": "CNIC is expired or expiry not found",
                    "document_type": DocumentType.ID_FRONT
                })
            if not license_expiry or license_expiry < date.today():
                errors.append({
                    "code": "LICENSE_EXPIRED_OR_INVALID",
                    "details": "License is expired or expiry not found",
                    "document_type": DocumentType.LICENSE_FRONT
                })

            # 5. Face Cropping & Matching
            try:
                face_cropped = self._crop_face(bundle.id_front)
                if not self._match_faces(bundle.selfie, face_cropped):
                    errors.append({
                        "code": "FACE_MISMATCH",
                        "details": f"Face distance >= {FACE_MATCH_THRESHOLD}",
                        "document_type": DocumentType.SELFIE_ID
                    })
            except ValueError as e:
                errors.append({
                    "code": "FACE_DETECTION_FAILED",
                    "details": str(e),
                    "document_type": DocumentType.SELFIE_ID
                })

        except MLProcessingError:
            raise
        except Exception as e:
            logger.exception("Identity engine crashed")
            errors.append({"code": "INTERNAL_ENGINE_ERROR", "details": str(e)})

        success = len(errors) == 0
        return VerificationResult(success=success, errors=errors, extracted_data=extracted)

    def _check_sizes(self, bundle: VerificationBundle) -> None:
        for name, data in [("id_front", bundle.id_front), ("selfie", bundle.selfie)]:
            size_mb = len(data) / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                raise ValueError(f"Image {name} exceeds {MAX_IMAGE_SIZE_MB}MB limit.")

    def _extract_ocr(self, image_bytes: bytes, cached_meta: dict[str, Any]) -> str:
        """Fetch from cache or run OCR."""
        if cached_meta and "ocr_text" in cached_meta:
            logger.info("Using cached OCR results")
            return cached_meta["ocr_text"]

        if not self.ocr:
            raise RuntimeError("PaddleOCR not loaded.")

        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise MLProcessingError("Corrupt or unsupported image for OCR.")

        result = self.ocr.ocr(img, cls=True)
        if not result or not result[0]:
            return ""

        text_lines = [line[1][0] for line in result[0] if line]
        return "\n".join(text_lines)

    def _extract_name_from_ocr(self, text: str) -> str:
        """Extracts the likely name string from full OCR text."""
        # Match only "name" keyword followed by letters/spaces on same line, avoid newline capture.
        pattern = r"(?i)^\s*name\s*[:=]?\s*([A-Za-z][A-Za-z ]{3,29})\s*$"
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            candidate = match.group(1).strip()
            if candidate:
                return candidate

        # Fallback: longest alphabetic line that looks like a name (>=2 words, <40 chars).
        best_line = ""
        for line in text.split('\n'):
            cleaned = re.sub(r'[^A-Za-z\s]', '', line).strip()
            if len(cleaned.split()) >= 2 and len(cleaned) < 40 and len(cleaned) > len(best_line):
                best_line = cleaned

        # Fail closed: if no plausible name line found, return empty so
        # cross-check surfaces NAME_MISMATCH instead of fuzzy-matching full OCR dumps.
        return best_line

    def _normalize_name(self, text: str) -> str:
        """Lowercases and removes common noise from names."""
        if not text:
            return ""
        text = text.lower().strip()
        # Keep common names but clean up special characters
        text = re.sub(r'[^a-z\s]', '', text)
        return " ".join(text.split())

    def _parse_date(self, text: str) -> date | None:
        """Parse date from OCR text using keywords and dateutil."""
        import dateutil.parser

        text_lower = text.lower()
        keywords = ["expiry", "date of expiry", "valid until", "valid upto"]

        search_windows = []
        for kw in keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                search_windows.append(text[idx:idx+40])

        search_windows.append(text) # Fallback to whole text

        patterns = [
            r"(\d{2}[-/.]\d{2}[-/.]\d{4})",
            r"(\d{4}[-/.]\d{2}[-/.]\d{2})",
            r"(\d{2}[-/.]\d{2}[-/.]\d{2})",
        ]

        for window in search_windows:
            for pattern in patterns:
                for match in re.findall(pattern, window):
                    try:
                        dt = dateutil.parser.parse(match, dayfirst=True)
                        return dt.date()
                    except (ValueError, OverflowError):
                        continue

        return None

    def _crop_face(self, image_bytes: bytes) -> np.ndarray:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise MLProcessingError("Corrupt or unsupported image for face detection.")
        faces = DeepFace.extract_faces(img, detector_backend='retinaface', enforce_detection=False)
        if not faces or len(faces) == 0:
            raise MLProcessingError("No face detected in ID.")

        if faces[0].get('confidence', 0) < 0.5:
            raise MLProcessingError("No face detected in ID with sufficient confidence.")

        face_data = faces[0]['face']

        # DeepFace extract_faces often returns normalized float32 [0, 1]
        # We need to ensure it's in a standard format or uint8 [0, 255] for consistency
        if face_data.dtype != np.uint8:
            if face_data.max() <= 1.0:
                face_data = (face_data * 255).astype(np.uint8)
            else:
                face_data = face_data.astype(np.uint8)

        return face_data

    def _match_faces(self, selfie_bytes: bytes, id_face_img: np.ndarray) -> bool:
        """Verify face match between selfie and cropped ID face."""
        np_arr = np.frombuffer(selfie_bytes, np.uint8)
        selfie_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if selfie_img is None:
            raise MLProcessingError("Corrupt or unsupported selfie image.")

        try:
            result = DeepFace.verify(
                img1_path=selfie_img,
                img2_path=id_face_img,
                model_name="Facenet512",
                enforce_detection=False,
                detector_backend='retinaface'
            )
            distance = result.get('distance', 1.0)
            logger.info(f"Face match distance: {distance}")
            return distance < FACE_MATCH_THRESHOLD
        except Exception as e:
            logger.warning(f"Face matching failed: {e}")
            raise MLProcessingError(f"Face matching could not be completed: {str(e)}") from e

    def _cross_check_names(self, *names: str) -> bool:
        if any(not name.strip() for name in names):
            return False
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                sim = fuzz.ratio(names[i], names[j])
                logger.info(f"Name similarity {names[i]} vs {names[j]}: {sim}")
                if sim < NAME_FUZZY_THRESHOLD:
                    return False
        return True
