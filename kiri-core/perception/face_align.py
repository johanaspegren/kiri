# modules/face_align.py
from __future__ import annotations
import numpy as np
import cv2

_ARCFACE_TEMPLATE_112 = np.array([
    [38.2946, 51.6963],
    [73.5318, 51.5014],
    [56.0252, 71.7366],
    [41.5493, 92.3655],
    [70.7299, 92.2041],
], dtype=np.float32)

def align_by_5pts(bgr_img, kps, out_size=(112,112)):
    """
    kps: list[(x,y)*5] order: left_eye, right_eye, nose, left_mouth, right_mouth
    returns aligned 112x112 BGR
    """
    dst = _ARCFACE_TEMPLATE_112.copy()
    if out_size != (112,112):
        scale_x = out_size[0] / 112.0
        scale_y = out_size[1] / 112.0
        dst *= np.array([scale_x, scale_y], dtype=np.float32)

    src = np.array(kps, dtype=np.float32)
    M, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.LMEDS)
    if M is None:
        # fallback: return a central crop resized
        h, w = bgr_img.shape[:2]
        s = min(h, w); y0 = (h - s)//2; x0 = (w - s)//2
        return cv2.resize(bgr_img[y0:y0+s, x0:x0+s], out_size, interpolation=cv2.INTER_LINEAR)
    return cv2.warpAffine(bgr_img, M, out_size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
