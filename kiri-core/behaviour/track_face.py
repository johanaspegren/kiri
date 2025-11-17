import asyncio
import time

class TrackFace:
    def __init__(
        self,
        motion,
        get_face_fn,
        pan_center=90,
        tilt_center=90,
        pan_gain=30.0,
        tilt_gain=25.0,
        box_smooth=0.35,
        lost_face_delay=1.0,
    ):
        """
        motion        : SwivelMotion instance
        get_face_fn   : function returning (x, y, w, h, frame_w, frame_h) or None
        pan_gain      : degrees of pan per normalized x error
        tilt_gain     : degrees of tilt per normalized y error
        box_smooth    : smoothing factor for box jitter
        lost_face_delay: time before releasing control when no face
        """

        self.motion = motion
        self.get_face = get_face_fn

        self.pan_center = pan_center
        self.tilt_center = tilt_center

        self.pan_gain = pan_gain
        self.tilt_gain = tilt_gain

        self.box_smooth = box_smooth
        self.last_bbox = None

        self.lost_face_delay = lost_face_delay
        self.last_seen_time = 0

    def _smooth_box(self, new_box):
        if self.last_bbox is None:
            self.last_bbox = new_box
            return new_box

        lx, ly, lw, lh = self.last_bbox
        nx, ny, nw, nh = new_box

        s = self.box_smooth
        smoothed = (
            lx + s*(nx-lx),
            ly + s*(ny-ly),
            lw + s*(nw-lw),
            lh + s*(nh-lh),
        )
        self.last_bbox = smoothed
        return smoothed

    async def loop(self, hz=20):
        dt = 1.0 / hz
        while True:
            face = self.get_face()

            now = time.monotonic()

            if face:
                x, y, w, h, W, H = face
                self.last_seen_time = now

                # Smooth the bounding box
                x, y, w, h = self._smooth_box((x, y, w, h))

                # Compute normalized error (cx, cy relative to frame center)
                cx = x + w/2
                cy = y + h/2
                ex = (cx - W/2) / (W/2)    # -1 … +1
                ey = (cy - H/2) / (H/2)    # -1 … +1

                # Convert into angles
                target_pan  = self.pan_center  + ex * self.pan_gain
                target_tilt = self.tilt_center + ey * self.tilt_gain

                # Update motion
                self.motion.set_target(target_pan, target_tilt)

            else:
                # No face
                if now - self.last_seen_time > self.lost_face_delay:
                    # Release control (later: hand off to search behaviour)
                    self.last_bbox = None

            await asyncio.sleep(dt)
