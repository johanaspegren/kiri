#!/usr/bin/env python3
import asyncio
import cv2

from hardware.swivel import SwivelController
from motion.swivel_motion import SwivelMotion
from motion.swivel_stable import SwivelMotionStable
from behaviour.track_face import TrackFace
from perception.face_provider import get_best_face
from perception.face_refiner import FaceRefiner
from hardware.imx500_detector import IMX500Detector
from config.models import YUNET
from runtime.web_preview import start_web_preview


class State:
    def __init__(self):
        self.frame = None
        self.faces = []


async def perception_loop(state, cam, fr):
    while True:
        frame_rgb = cam.capture_rgb()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        faces = fr.detect_faces(frame)

        state.frame = frame
        state.faces = faces

        await asyncio.sleep(0)


async def main():
    print("=== KIRI Face Tracker Test ===")

    state = State()

    cam = IMX500Detector()
    cam.start(show_preview=False)

    fr = FaceRefiner(YUNET)

    sw = SwivelController().open()
    raw_motion = SwivelMotion(sw)        # your original class
    motion = SwivelMotionStable(raw_motion)

    asyncio.create_task(raw_motion.loop())

    tracker = TrackFace(
        motion=motion,
        get_face_fn=lambda: get_best_face(state),
        pan_gain=-40.0,
        tilt_gain=+35.0
    )
    asyncio.create_task(tracker.loop())

    asyncio.create_task(perception_loop(state, cam, fr))

    await start_web_preview(state, port=8080)

    print("Move your head — KIRI is watching you!")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

