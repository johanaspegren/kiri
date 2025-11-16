# modules/imx500_detector.py
import cv2, numpy as np
from pathlib import Path
from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics, postprocess_nanodet_detection

from config.models import COCO_LABELS_PATH

#ASSETS = Path("assets")  # so it works regardless of CWD

class IMX500Detector:
    def __init__(self, model_path="/usr/share/imx500-models/imx500_network_yolo11n_pp.rpk"):
#    def __init__(self, model_path="/usr/share/imx500-models/imx500_network_yolov8n_pp.rpk"):
#    def __init__(self, model_path="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk"):
        self.last_detections = []
        self.last_results = None

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

        self.picam2 = Picamera2(self.imx500.camera_num)

    def start(self, show_preview=True):
        cfg = self.picam2.create_preview_configuration(
            controls={"FrameRate": self.intrinsics.inference_rate},
            buffer_count=12
        )
        self.imx500.show_network_fw_progress_bar()
        self.picam2.start(cfg, show_preview=show_preview)
        if self.intrinsics.preserve_aspect_ratio:
            self.imx500.set_auto_aspect_ratio()
        self.picam2.pre_callback = self._draw_detections

    def stop(self):
        self.picam2.stop()

    def get_detections(self):
        self.last_results = self._parse_detections(self.picam2.capture_metadata())
        return self.last_results

    def get_labels(self):
        labels = self.intrinsics.labels
        #if self.intrinsics.ignore_dash_labels:
        #    labels = [l for l in labels if l and l != "-"]
        return labels

    def _parse_detections(self, metadata):
        # Kinder, gentler thresholds
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
            # Generic path: [boxes, scores, classes]
            boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
            boxes = boxes.astype(np.float32, copy=False)
            if bbox_norm:
                # Correct scaling: x,w by width; y,h by height
                boxes[:, [0, 2]] *= float(input_w)
                boxes[:, [1, 3]] *= float(input_h)
            # keep boxes as Nx4 (x,y,w,h)

        labels = self.get_labels() or []
        dets = []
        n = min(len(scores), len(boxes), len(classes), MAX_DETS)
        for i in range(n):
            s = float(scores[i])
            if s < THRESH:
                continue
            cls = int(classes[i])
            # guard against weird indices
            name = labels[cls] if 0 <= cls < len(labels) else f"class_{cls}"
            x, y, w, h = map(float, boxes[i])
            coords = np.array([x, y, w, h], dtype=np.float32)
            dets.append(Detection(coords, cls, s, metadata, self.imx500, self.picam2))

        # lightweight telemetry if we kept nothing
        if not dets:
            raw = len(scores)
            mx = float(np.max(scores)) if raw else 0.0
            uc = sorted({int(c) for c in classes[:min(raw, 20)]}) if raw else []
            print(f"[imx500] raw={raw} max={mx:.2f} classes={uc} labels={len(labels)}")
        self.last_detections = dets
        return dets


    def _draw_detections(self, request, stream="main"):
        if self.last_results is None:
            return
        labels = self.get_labels()
        with MappedArray(request, stream) as m:
            for d in self.last_results:
                x, y, w, h = d.box
                label = f"{labels[int(d.category)]} ({float(d.conf):.2f})"
                (tw, th), base = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                tx, ty = x + 5, y + 15
                overlay = m.array.copy()
                cv2.rectangle(overlay, (tx, ty - th), (tx + tw, ty + base), (255, 255, 255), cv2.FILLED)
                cv2.addWeighted(overlay, 0.30, m.array, 0.70, 0, m.array)
                cv2.putText(m.array, label, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0, 0), 2)

class Detection:
    def __init__(self, coords, category, conf, metadata, imx500, picam2):
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)
