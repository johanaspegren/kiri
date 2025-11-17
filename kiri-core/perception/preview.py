import cv2
import asyncio

async def preview_loop(state, window_name="KIRI Preview", hz=12):
    """
    Shows live feed with bounding boxes.
    Non-blocking: runs at ~10-12 FPS to avoid slowing system.
    """
    dt = 1.0 / hz
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        frame = state.frame
        faces = state.faces

        if frame is not None:
            shown = frame.copy()

            if faces:
                for face in faces:
                    x, y, w, h = face["box"]
                    cv2.rectangle(shown, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow(window_name, shown)

        # process GUI events — non-blocking
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        await asyncio.sleep(dt)

    cv2.destroyAllWindows()
