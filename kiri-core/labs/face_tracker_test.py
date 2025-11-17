#!/usr/bin/env python3
import asyncio
import cv2

from hardware.swivel import SwivelController
from motion.swivel_motion import SwivelMotion
from behaviour.track_face import TrackFace
from perception.face_provider import get_best_face

# your perception modules
from perception.face_refiner import FaceRefiner
#from perception.preview import preview_loop
from hardware.imx500_detector import IMX500Detector

from config.models import YUNET, EMBEDDER

# web preview
from runtime.web_preview import start_web_preview



class State:
    """Shared state between perception and behaviour."""
    def __init__(self):
        self.frame = None
        self.faces = []


async def perception_loop(state, cam, fr):
    """Continuously grab frames and run face detection."""
    while True:

        frame_rgba = cam.picam2.capture_array()

        # Drop alpha/X channel if present
        if frame_rgba.shape[2] == 4:
            frame_rgb = frame_rgba[:, :, :3]
        else:
            frame_rgb = frame_rgba

        # Convert RGB → BGR for OpenCV YuNet
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)


        faces = fr.detect_faces(frame)

        state.frame = frame
        state.faces = faces

        await asyncio.sleep(0)   # yield to event loop

async def main():
    print("=== Face Tracker Test with Web Preview ===")

    state = State()

    cam = IMX500Detector()
    cam.start(show_preview=False)

    fr = FaceRefiner(YUNET)

    sw = SwivelController().open()
    motion = SwivelMotion(sw)
    asyncio.create_task(motion.loop())

    tracker = TrackFace(
        motion=motion,
        get_face_fn=lambda: get_best_face(state),
        pan_gain=-30.0,
        tilt_gain=+25.0
    )
    asyncio.create_task(tracker.loop())

    asyncio.create_task(perception_loop(state, cam, fr))
    #asyncio.create_task(preview_loop(state, hz=12))   # ⬅ HERE

    # Web preview
    await start_web_preview(state, port=8080)

    print("Move your head — KIRI is watching you!")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
