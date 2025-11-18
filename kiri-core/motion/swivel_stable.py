# motion/swivel_stable.py
# Serenity for servos since 2025.

import math

class SwivelMotionStable:
    """
    A wrapper that stabilises target commands to SwivelMotion.
    It adds:
      - dead zone
      - low-pass smoothing
      - max per-update step limit
    """

    def __init__(
        self,
        inner_motion,
        deadzone_deg=1.2,
        smooth_alpha=0.25,
        max_step_deg=3.0,
    ):
        self.m = inner_motion  # the existing SwivelMotion instance

        self.deadzone = deadzone_deg
        self.alpha = smooth_alpha
        self.max_step = max_step_deg

        self.stab_pan = None
        self.stab_tilt = None

    def set_target(self, pan, tilt):
        """
        Applies smoothing + dead zone + step limiting.
        Called instead of inner_motion.set_target().
        """

        # Initialise stabilised targets
        if self.stab_pan is None:
            self.stab_pan = float(pan)
            self.stab_tilt = float(tilt)
            self.m.set_target(self.stab_pan, self.stab_tilt)
            return

        pan = float(pan)
        tilt = float(tilt)

        # --- Dead zone ---
        pan_err = pan - self.stab_pan
        tilt_err = tilt - self.stab_tilt

        if abs(pan_err) < self.deadzone:
            pan = self.stab_pan
        if abs(tilt_err) < self.deadzone:
            tilt = self.stab_tilt

        # --- Low-pass smoothing ---
        sm_pan = self.stab_pan + self.alpha * (pan - self.stab_pan)
        sm_tilt = self.stab_tilt + self.alpha * (tilt - self.stab_tilt)

        # --- Max step limiting ---
        def clamp(prev, nxt):
            diff = nxt - prev
            if abs(diff) > self.max_step:
                return prev + math.copysign(self.max_step, diff)
            return nxt

        final_pan = clamp(self.stab_pan, sm_pan)
        final_tilt = clamp(self.stab_tilt, sm_tilt)

        # update stabilised values
        self.stab_pan = final_pan
        self.stab_tilt = final_tilt

        # pass down to the real SwivelMotion
        self.m.set_target(final_pan, final_tilt)
