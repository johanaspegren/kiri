from pathlib import Path

from pathlib import Path

# Find the project root by locating the folder that contains "models/"
_current = Path(__file__).resolve()
while _current != _current.parent:
    if (_current / "models").exists():
        ROOT = _current
        break
    _current = _current.parent
else:
    raise RuntimeError("Could not locate the 'models' directory.")


MODELS = ROOT / "models"

FACE = MODELS / "face"
DETECTION = MODELS / "detection"
AUDIO = MODELS / "audio"
CV = MODELS / "cv"

COCO_LABELS_PATH = CV / "coco_labels.txt"
YUNET = FACE / "face_detection_yunet_2023mar.onnx"
EMBEDDER = FACE / "w600k_r50.onnx"
PIPER_VOICE = AUDIO / "piper_voice.onnx"
PIPER_CONFIG = AUDIO / "piper_voice.onnx.json"
