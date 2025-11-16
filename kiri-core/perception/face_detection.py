import cv2
import asyncio
from modules.face_refiner import FaceRefiner

class FaceDetector:
    """
    A simple async face detector using YuNet.
    Returns: list[ {"box": [x,y,w,h], "kps": [...]} ]
    """

    def __init__(self, yunet_path):
        self.detector = FaceRefiner(str(yunet_path))

    async def detect(self, frame_rgb):
        # convert to BGR for YuNet
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        faces = self.detector.detect_faces(frame_bgr)
        return faces
