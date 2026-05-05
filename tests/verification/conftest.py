from __future__ import annotations

import sys
import types
from typing import Any, cast


class _StubDeepFace:
    @staticmethod
    def verify(*args, **kwargs):
        return {"verified": True, "distance": 0.1}

    @staticmethod
    def extract_faces(*args, **kwargs):
        return []


deepface_module = types.ModuleType("deepface")
cast(Any, deepface_module).DeepFace = _StubDeepFace
sys.modules.setdefault("deepface", deepface_module)

paddleocr_module = types.ModuleType("paddleocr")
cast(Any, paddleocr_module).PaddleOCR = lambda *args, **kwargs: None
sys.modules.setdefault("paddleocr", paddleocr_module)
