# modules/face_embedder.py
from __future__ import annotations
import numpy as np
import cv2, onnxruntime as ort
from pathlib import Path

class FaceEmbedder:
    def __init__(self, onnx_path: str | Path):
        self.onnx = str(onnx_path)
        self.session = ort.InferenceSession(self.onnx, providers=["CPUExecutionProvider"])
        io = self.session.get_inputs()[0]
        self.in_name = io.name
        self.in_shape = io.shape  # [1,3,112,112] typically
        self.out_name = self.session.get_outputs()[0].name

    def preprocess(self, bgr_face: np.ndarray, size=(112,112)):
        # convert to RGB, resize, normalise to [-1,1] or [0,1] depending on model
        img = cv2.cvtColor(bgr_face, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, size, interpolation=cv2.INTER_LINEAR)
        img = img.astype(np.float32) / 127.5 - 1.0  # [-1,1] common for InsightFace
        # NCHW
        img = np.transpose(img, (2,0,1))[None, ...]
        return img

    def embed(self, bgr_face: np.ndarray) -> np.ndarray:
        inp = self.preprocess(bgr_face)
        out = self.session.run([self.out_name], {self.in_name: inp})[0][0]
        # L2-normalise so cosine similarity behaves
        v = out / (np.linalg.norm(out) + 1e-9)
        return v.astype(np.float32)
