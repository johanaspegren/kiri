import asyncio
import time
import math

class SwivelMotion:
    def __init__(self, controller, hz=30, max_speed=120):
        """
        controller: SwivelController instance
        hz: control loop frequency
        max_speed: degrees per second
        """
        self.controller = controller
        self.hz = hz
        self.max_speed = max_speed

        self.current_pan = 90
        self.current_tilt = 90
        self.target_pan = 90
        self.target_tilt = 90

        self.running = False

    def set_target(self, pan: float, tilt: float):
        self.target_pan = float(pan)
        self.target_tilt = float(tilt)

    async def loop(self):
        self.running = True
        dt = 1 / self.hz

        while self.running:
            start = time.monotonic()

            # compute next step
            next_pan = self._step_towards(self.current_pan, self.target_pan, dt)
            next_tilt = self._step_towards(self.current_tilt, self.target_tilt, dt)

            self.current_pan = next_pan
            self.current_tilt = next_tilt

            # send to hardware
            self.controller.set(self.current_pan, self.current_tilt)

            # sleep accurately
            elapsed = time.monotonic() - start
            await asyncio.sleep(max(0, dt - elapsed))

    def _step_towards(self, current, target, dt):
        max_step = self.max_speed * dt
        diff = target - current

        if abs(diff) <= max_step:
            return target
        return current + math.copysign(max_step, diff)
