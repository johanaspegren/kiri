import asyncio
import threading
import cv2
from hardware.imx500_detector import IMX500Detector

class CameraPipeline:
    """
    A threaded, non-blocking camera pipeline.
    Produces RGB frames via an asyncio.Queue.
    """

    def __init__(self, queue_size=2, show_preview=False):
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.show_preview = show_preview
        self.stop_flag = False

        self.cam = IMX500Detector()

    def start(self):
        self.cam.start(show_preview=self.show_preview)

        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def stop(self):
        self.stop_flag = True
        self.cam.stop()

    def _loop(self):
        """Runs in a background thread, pushing frames into the async queue."""
        while not self.stop_flag:
            try:
                rgb = self.cam.picam2.capture_array()
                self.queue.put_nowait(rgb)
            except asyncio.QueueFull:
                pass

    async def get_frame(self):
        return await self.queue.get()
