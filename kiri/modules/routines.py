import time
import random

class KiriRoutines:
    """
    High-level behavioural routines for KIRI.
    These combine motions, speech, and sequencing.
    """

    def __init__(self, motions, tts=None):
        self.motions = motions
        self.tts = tts

    def wake_up(self):
        """KIRI's expressive wake-up ritual."""
        
        # 1. Center motion
        self.motions.center()
        time.sleep(0.35)

        # 2. Stretch gesture
        self.motions.nod_small()

        # 3. Greet vocally (optional)
        if self.tts:
            self.tts.say("Hi, I'm Kiri.")
        
        # 4. Wakeful scanning
        for ang in [70, 110, 85, 100, 90]:
            self.motions.glance(ang, pause=0.28)

        # 5. Micro-adjust for realism
        jitter = random.randint(-3, 3)
        self.motions.set_pan(90 + jitter)
        time.sleep(0.15)
