# hardware/imx500_detector.py

import cv2, numpy as np
from pathlib import Path
from picamera2 import Picamera2, MappedArray
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics, postprocess_nanodet_detection

from config.models import COCO_LABELS_PATH


class IMX500Detector:
    """
    Single, unified IMX500 + Picamera2 camera.

    - IMX500 metadata used for object/person detection
    - Picamera2 main stream (640x480 RGB) used for YuNet face detection
    - No second Picamera2 instance (this avoids allocator crashes)
    - Fully compatible with TrackFace and SwivelMotion
    """

    def __init__(self,
                 model_path="/usr/share/imx500-models/imx500_network_yolo11n_pp.rpk",
                 rgb_size=(640, 480)):

        self.last_detections = []
        self.last_results = None
        self.rgb_size = rgb_size

        # --- IMX500 setup ---
        self.imx500 = IMX500(model_path)
        self.intrinsics = self.imx500.network_intrinsics or NetworkIntrinsics()

        if not self.intrinsics.task:
            self.intrinsics.task = "object detection"
        elif self.intrinsics.task != "object detection":
            raise ValueError("Network is not an object detection task")

        if self.intrinsics.labels is None:
            with open(COCO_LABELS_PATH, "r") as f:
                self.intrinsics.labels = f.read().splitlines()

        self.intrinsics.ignore_dash_labels = False
        self.intrinsics.preserve_aspect_ratio = True
        self.intrinsics.update_with_defaults()

        # The IMX500 camera number is required
        self.picam2 = Picamera2(self.imx500.camera_num)


    def start(self, show_preview=False):
        """
        Configure ONE camera with TWO streams:
          - main: clean RGB (640x480) for face detection
          - lores: tiny preview (320x240) for optional web preview overlay
        """

        config = self.picam2.create_video_configuration(
            main={
                "size": self.rgb_size,
                "format": "RGB888"
            },
            lores={
                "size": (320, 240),
                "format": "RGB888"
            },
            controls={"FrameRate": 30},
            buffer_count=8
        )

        # Upload IMX500 network firmware
        self.imx500.show_network_fw_progress_bar()

        self.picam2.configure(config)
        self.picam2.start(show_preview=show_preview)

        if self.intrinsics.preserve_aspect_ratio:
            self.imx500.set_auto_aspect_ratio()

        # Overlay IMX500 detections on lores stream (optional)
        self.picam2.pre_callback = self._draw_detections


    def stop(self):
        self.picam2.stop()


    # --- clean RGB frame for YuNet ---
    def capture_rgb(self):
        """Return a clean RGB frame (640x480) for YuNet."""
        return self.picam2.capture_array("main")


    # ========== IMX500 detection parsing ==========

    def get_detections(self):
        """IMX500 person/object detections."""
        self.last_results = self._parse_detections(self.picam2.capture_metadata())
        return self.last_results

    def get_labels(self):
        return self.intrinsics.labels or []


    def _parse_detections(self, metadata):
        THRESH, IOU, MAX_DETS = 0.22, 0.45, 20

        np_outputs = self.imx500.get_outputs(metadata, add_batch=True)
        if np_outputs is None:
            return self.last_detections

        input_w, input_h = self.imx500.get_input_size()
        bbox_norm = bool(self.intrinsics.bbox_normalization)
        postproc = (self.intrinsics.postprocess or "").lower()

        if postproc == "nanodet":
            boxes, scores, classes = postprocess_nanodet_detection(
                outputs=np_outputs[0], conf=THRESH, iou_thres=IOU, max_out_dets=MAX_DETS
            )[0]
            from picamera2.devices.imx500.postprocess import scale_boxes
            boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
        else:
            boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
            boxes = boxes.astype(np.float32, copy=False)
            if bbox_norm:
                boxes[:, [0, 2]] *= float(input_w)
                boxes[:, [1, 3]] *= float(input_h)

        labels = self.get_labels()
        dets = []
        n = min(len(scores), len(boxes), len(classes), MAX_DETS)

        for i in range(n):
            s = float(scores[i])
            if s < THRESH:
                continue

            cls = int(classes[i])
            x, y, w, h = map(float, boxes[i])
            coords = np.array([x, y, w, h], dtype=np.float32)

            dets.append(Detection(coords, cls, s, metadata, self.imx500, self.picam2))

        self.last_detections = dets
        return dets


    # --- draw IMX500 detections on lores preview ---
    def _draw_detections(self, request, stream="lores"):
        if self.last_results is None:
            return

        labels = self.get_labels()

        with MappedArray(request, stream) as m:
            for d in self.last_results:
                x, y, w, h = d.box
                label = f"{labels[d.category]} {d.conf:.2f}"
                cv2.rectangle(m.array, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(m.array, label, (x, max(15, y-4)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0,255,0), 1)


class Detection:
    def __init__(self, coords, category, conf, metadata, imx500, picam2):
        self.category = category
        self.conf = conf

        # convert inference coords → image coords
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)
