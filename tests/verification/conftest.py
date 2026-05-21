from __future__ import annotations

import sys
import types
from typing import Any, cast


class _FakeImage:
    dtype = "uint8"

    def max(self) -> float:
        return 255.0

    def astype(self, *_args: Any, **_kwargs: Any) -> "_FakeImage":
        return self


numpy_module = types.ModuleType("numpy")
cast(Any, numpy_module).uint8 = "uint8"
cast(Any, numpy_module).ndarray = _FakeImage
cast(Any, numpy_module).frombuffer = lambda *_args, **_kwargs: _FakeImage()
cast(Any, numpy_module).zeros = lambda *_args, **_kwargs: _FakeImage()
sys.modules["numpy"] = numpy_module


cv2_module = types.ModuleType("cv2")
cast(Any, cv2_module).IMREAD_COLOR = 1
cast(Any, cv2_module).imdecode = lambda *_args, **_kwargs: _FakeImage()
sys.modules["cv2"] = cv2_module


class _StubDeepFace:
    @staticmethod
    def verify(*args, **kwargs):
        return {"verified": True, "distance": 0.1}

    @staticmethod
    def extract_faces(*args, **kwargs):
        return []


deepface_module = types.ModuleType("deepface")
cast(Any, deepface_module).DeepFace = _StubDeepFace
sys.modules["deepface"] = deepface_module

paddleocr_module = types.ModuleType("paddleocr")
cast(Any, paddleocr_module).PaddleOCR = lambda *args, **kwargs: None
sys.modules["paddleocr"] = paddleocr_module

rapidfuzz_module = types.ModuleType("rapidfuzz")
fuzz_module = types.ModuleType("rapidfuzz.fuzz")
cast(Any, fuzz_module).ratio = lambda *_args, **_kwargs: 100.0
cast(Any, rapidfuzz_module).fuzz = fuzz_module
sys.modules["rapidfuzz"] = rapidfuzz_module
sys.modules["rapidfuzz.fuzz"] = fuzz_module
