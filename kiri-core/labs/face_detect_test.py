#!/usr/bin/env python3
import cv2
import numpy as np
from pathlib import Path


from hardware.imx500_detector import IMX500Detector
from perception.face_refiner import FaceRefiner
from config.models import YUNET, EMBEDDER



def main():
    print("Starting IMX500 + YuNet face detection test…")

    # Initialise camera
    cam = IMX500Detector()
    cam.start(show_preview=False)

    # Initialise YuNet detector
    fd = FaceRefiner(str(YUNET), score=0.30, nms=0.3, model_in=(416,416))

    print("Camera ready. Showing detections… (Ctrl+C to exit)")

    try:
        while True:
            # Capture RGB frame
            frame_rgb = cam.picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # Detect faces
            faces = fd.detect_faces(frame_bgr)

            if faces:
                print(f"[det] detected {len(faces)} face(s)")
            else:
                print("[det] no face")

            # Optional on-screen preview with rectangles
            for f in faces:
                x,y,w,h = f["box"]
                cv2.rectangle(frame_bgr, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(frame_bgr, "face", (x, y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            cv2.imshow("Face Detection Test", frame_bgr)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        print("\nStopping…")

    finally:
        cam.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
