import time

class KiriMotions:
    """
    Low-level movement primitives.
    No TTS. No sequences lasting > 1 step.
    """

    def __init__(self, swivel):
        self.swivel = swivel

    def center(self):
        self.swivel.set(90, 90)

    def set_pan(self, angle):
        self.swivel.set(angle, 90)

    def glance(self, angle, tilt=90, pause=0.25):
        self.swivel.set(angle, tilt)
        time.sleep(pause)

    def nod_small(self):
        self.swivel.tilt(-4); time.sleep(0.15)
        self.swivel.tilt(+6); time.sleep(0.18)
        self.swivel.tilt(-2); time.sleep(0.12)
