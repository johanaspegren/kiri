import asyncio
import time
import math


class TrackFace:
    """
    Advanced face-tracking controller with:
      - Adaptive box smoothing
      - Nonlinear gain shaping (stable near centre, strong at edges)
      - Edge boosting for fast recentering
      - Anti-oscillation behavior
    """

    def __init__(
        self,
        motion,
        get_face_fn,
        pan_center=90,
        tilt_center=60,
        pan_gain=40.0,      # baseline gain (safe, stable)
        tilt_gain=35.0,
        box_smooth=0.20,    # initial smoothing for jitter
        lost_face_delay=1.0,
    ):
        self.motion = motion
        self.get_face = get_face_fn

        self.pan_center = float(pan_center)
        self.tilt_center = float(tilt_center)

        # base gains
        self.base_pan_gain = float(pan_gain)
        self.base_tilt_gain = float(tilt_gain)

        self.box_smooth = float(box_smooth)
        self.last_bbox = None

        self.lost_face_delay = float(lost_face_delay)
        self.last_seen_time = 0


    # -------------------------------------------------------------
    # Adaptive smoothing (jitter gets smoothed, real movement does not)
    # -------------------------------------------------------------
    def _smooth_box(self, new_box):
        if self.last_bbox is None:
            self.last_bbox = new_box
            return new_box

        lx, ly, lw, lh = self.last_bbox
        nx, ny, nw, nh = new_box

        # detect real movement by center shift
        prev_cx = lx + lw/2
        new_cx  = nx + nw/2
        delta_cx = abs(new_cx - prev_cx)

        # If user moves head fast → reduce smoothing
        if delta_cx > 15:
            s = 0.05
        else:
            s = self.box_smooth

        smoothed = (
            lx + s*(nx - lx),
            ly + s*(ny - ly),
            lw + s*(nw - lw),
            lh + s*(nh - lh),
        )

        self.last_bbox = smoothed
        return smoothed


    # -------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------
    async def loop(self, hz=20):
        dt = 1.0 / hz

        while True:
            now = time.monotonic()
            face = self.get_face()

            if face:
                x, y, w, h, W, H = face
                self.last_seen_time = now

                # Smooth bbox
                x, y, w, h = self._smooth_box((x, y, w, h))

                # Compute face center
                cx = x + w/2
                cy = y + h/2

                # Normalized errors
                ex = (cx - W/2) / (W/2)
                ey = (cy - H/2) / (H/2)

                # -----------------------------
                # Nonlinear gain shaping
                # -----------------------------
                abs_ex = abs(ex)

                if abs_ex < 0.10:
                    pan_gain = self.base_pan_gain * 0.6    # gentle
                elif abs_ex < 0.30:
                    pan_gain = self.base_pan_gain * 1.0    # normal
                elif abs_ex < 0.60:
                    pan_gain = self.base_pan_gain * 1.8    # strong
                else:
                    pan_gain = self.base_pan_gain * 2.5    # full authority

                # Edge boosting (smooth in center, strong near edges)
                ex_shaped = ex * (1.0 + abs_ex)

                # Tilt: keep linear (tilt is usually more stable)
                tilt_gain = self.base_tilt_gain
                ey_shaped = ey * (1.0 + abs(ey)*0.2)

                # Convert to angles
                target_pan  = self.pan_center  + ex_shaped * pan_gain
                target_tilt = self.tilt_center + ey_shaped * tilt_gain

                # DEBUG:
                # print(f"W:{W} cx:{cx:.1f} ex:{ex:.3f} gain:{pan_gain:.1f} target_pan:{target_pan:.1f}")

                self.motion.set_target(target_pan, target_tilt)

            else:
                # No face detected
                if now - self.last_seen_time > self.lost_face_delay:
                    self.last_bbox = None

            await asyncio.sleep(dt)
