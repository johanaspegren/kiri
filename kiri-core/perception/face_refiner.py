# modules/face_refiner.py
from pathlib import Path
import cv2
import numpy as np

class FaceRefiner:
    """
    YuNet-first face detector with an adaptive fallback pass.
    Returns list of dicts: {"box":[x,y,w,h], "kps":[(x1,y1),...,(x5,y5)]}
    """
    def __init__(self, yunet_path: str, score=0.30, nms=0.3, require_yunet: bool = True, model_in=(416, 416)):
        p = Path(yunet_path)
        if not p.exists() or p.stat().st_size == 0:
            if require_yunet:
                raise FileNotFoundError(f"YuNet ONNX missing: {p}")
            raise RuntimeError("YuNet required but not available.")
        # ensure ONNX is readable
        cv2.dnn.readNetFromONNX(str(p))
        self.det = cv2.FaceDetectorYN.create(
            model=str(p),
            config="",
            input_size=tuple(model_in),
            score_threshold=float(score),
            nms_threshold=float(nms),
            top_k=5000,
        )
        self.base_score = float(score)
        self.mode = "yunet"

    def _preproc_boost(self, bgr: np.ndarray) -> np.ndarray:
        img = bgr.astype(np.float32) / 255.0
        img = np.clip(img ** 0.8, 0, 1)              # gamma lift
        img = (img * 255).astype(np.uint8)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(l)
        return cv2.cvtColor(cv2.merge([l,a,b]), cv2.COLOR_LAB2BGR)

    def _run(self, bgr_img: np.ndarray, score=None):
        h, w = bgr_img.shape[:2]
        self.det.setInputSize((w, h))
        if score is not None:
            self.det.setScoreThreshold(score)
        _, dets = self.det.detect(bgr_img)
        faces = []
        if dets is not None:
            # YuNet returns [x,y,w,h, l0x,l0y, l1x,l1y, ..., l4x,l4y, score]
            for arr in dets:
                arr = arr.tolist()
                x, y, ww, hh = map(int, arr[:4])
                kps = [(int(arr[4+i*2]), int(arr[5+i*2])) for i in range(5)]
                # clamp
                x = max(0, min(x, w-1)); y = max(0, min(y, h-1))
                ww = max(1, min(ww, w - x)); hh = max(1, min(hh, h - y))
                faces.append({"box":[x,y,ww,hh], "kps":kps})
        return faces

    def detect_faces(self, bgr_img: np.ndarray):
        faces = self._run(bgr_img, score=self.base_score)
        if faces:
            return faces
        boosted = self._preproc_boost(bgr_img)
        return self._run(boosted, score=max(0.15, self.base_score - 0.10))
