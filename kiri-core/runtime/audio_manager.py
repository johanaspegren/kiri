import asyncio
from hardware.piper_tts import TTS

class AudioManager:
    """
    A non-blocking audio manager for Piper TTS.

    - Maintains an async queue of messages to speak.
    - Executes Piper in a separate thread (since Piper blocks).
    - Ensures no overlapping speech unless explicitly allowed.
    """

    def __init__(self):
        self.tts = TTS()
        self.queue = asyncio.Queue()
        self.running = False

    async def start(self):
        """Start the audio loop."""
        if self.running:
            return
        self.running = True
        asyncio.create_task(self._audio_loop())

    async def say(self, text: str):
        """Public method — enqueue a speech request."""
        await self.queue.put(text)

    async def _audio_loop(self):
        """Background loop: processes speech requests continuously."""
        while self.running:
            text = await self.queue.get()

            # Offload Piper blocking call to a thread
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.tts.say, text)

            self.queue.task_done()
