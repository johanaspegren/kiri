import asyncio
import cv2
import numpy as np
from aiohttp import web

async def mjpeg_stream(state):
    """
    Async generator that yields JPEG frames with bounding boxes.
    """
    while True:
        frame = state.frame

        if frame is None:
            await asyncio.sleep(0.01)
            continue

        shown = frame.copy()

        # Draw bounding boxes
        faces = getattr(state, "faces", [])
        for f in faces:
            x, y, w, h = f["box"]
            cv2.rectangle(shown, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Encode JPEG
        ret, jpeg = cv2.imencode('.jpg', shown, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
        if not ret:
            continue

        frame_bytes = jpeg.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               frame_bytes +
               b"\r\n")
        
        await asyncio.sleep(0.03)   # ~30 FPS max


async def handle_mjpeg(request):
    state = request.app["state"]
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            "Content-Type": "multipart/x-mixed-replace; boundary=frame"
        }
    )
    await response.prepare(request)

    async for frame in mjpeg_stream(state):
        await response.write(frame)

    return response


async def start_web_preview(state, host="0.0.0.0", port=8080):
    """
    Launches the tiny web server for preview streaming.
    """
    app = web.Application()
    app["state"] = state
    app.router.add_get("/", handle_mjpeg)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    print(f"[Preview] Web preview running at http://{host}:{port}")
