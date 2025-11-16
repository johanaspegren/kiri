# ⭐ KIRI — A Tiny Curious Companion Powered by KIRI Core

A small, perceptive robotic creature with curiosity, presence-awareness, and expressive motion.

KIRI, think of a tiny kinetic creature that wakes up, looks around, recognizes familiar faces, greets returning humans, reacts with subtle gestures, and can chat using an LLM.
Designed to feel alive — not humanoid, not cartoonish — but like a small intelligent animal or house spirit.

**KIRI is powered by KIRI Core**, a modular framework for interactive robotic intelligence.

## 🌱 What is KIRI?

KIRI is a perceptive, expressive, behavior-driven micro-robot running on a Raspberry Pi with:

- a pan–tilt head
- a camera (IMX500 / PiCam2)
- local TTS (Piper)
- face recognition (yunet)
- presence tracking
- expressive gestures
- animated wake/sleep rituals
- LLM-based conversation

KIRI (is intended to) behave like a small curious creature — a cross between:

- a pika
- an otter
- a ferret
- and a Nordic house spirit

It watches, recognizes, greets, and responds.

## 🧬 Personality & Design Philosophy

KIRI should feel:

- small
- curious
- attentive
- cuddly but not childish
- a bit mischievous
- alive

It doesn't aim to be humanoid.
Instead, KIRI behaves like a tiny, perceptive creature that shares your space.

## 🧠 What is KIRI Core?

Kernel for Interactive Robotic Intelligence**

It is the underlying framework that powers KIRI's:

- perception
- motion
- routines
- behaviors
- state transitions
- context awareness
- audio output
- integrations (LLM, OCR, etc.)

KIRI Core is modular, scalable, and designed to support additional sensors, behaviours, and "creature-like" interactions.

## 🧱 Folder Structure

```
kiri/
│
├── core/                     # brain
│   ├── event_bus.py          # pub/sub message system
│   ├── state_machine.py      # Idle / Searching / Tracking / Talking / Sleeping
│   ├── behaviour_engine.py   # chooses what KIRI does next
│   ├── presence.py           # tracks who/when/return logic
│   └── config.py
│
├── modules/                  # body + senses
│   ├── swivel.py             # servo controller
│   ├── motions.py            # small movement primitives
│   ├── routines.py           # high-level sequences (wake-up, greet, sleep)
│   ├── tts.py                # Piper TTS with auto USB/Bluetooth routing
│   ├── camera_stream.py      # IMX500/PiCam capture
│   ├── face_detect.py        # detection + refinement
│   ├── face_id.py            # embeddings + DB
│   ├── ocr.py                # optional OCR
│   └── llm_agent.py          # chat logic
│
├── app/
│   ├── main.py               # starts everything
│   └── supervisor.py         # robustness & graceful shutdown
│
├── scripts/                  # standalone utilities or tests
│   └── test_wakeup.py
│
├── assets/
│   ├── face_db/              # embeddings & stored identities
│   └── tts_cache/
│
└── pyproject.toml            # makes KIRI installable (pip install -e .)
```



## 🔍 Presence & Greeting Logic

KIRI remembers:

- who it saw
- for how long
- when they left
- when they return

If you come back after a while, it will greet you warmly.
If you leave briefly, it won't spam greetings like an over-enthusiastic puppy.

## 🧠 Behavior Engine

The Behaviour Engine manages KIRI's brain state:

### States:

- **Idle** (resting, tiny micro-motions)
- **Searching** (scanning for humans)
- **Tracking** (following a detected face)
- **Talking** (LLM dialog mode)
- **Sleeping** (rest gesture, shutdown)

### Events:

Handled via the Event Bus:

- `FACE_DETECTED`
- `FACE_LOST`
- `PERSON_IDENTIFIED`
- `PERSON_RETURNED`
- `SYSTEM_WAKE`
- `SYSTEM_SLEEP`
- `GREET`
- `CHAT_REQUEST`

## 🎤 Audio System

KIRI uses Piper TTS, with prio-based output routing:

1. USB speaker on `hw:2,0`
2. Bluetooth A2DP sink
3. Default PulseAudio/pipewire sink

This should guarantee that KIRI always has a voice.

## 🐾 Motion Philosophy

KIRI's movements use the small-creature model:

- quick micro-nods
- curious glances
- slow scanning arcs
- slight jitter / micro-adjustments
- center→tilt→return patterns

Movements should feel alive, non-robotic, and gently expressive.

## 🤖 Chatting With KIRI

The module `llm_agent.py` handles:

- LLM interactions
- contextual conversation
- memory of recent dialog
- voice output pipeline

Using streaming models from OpenAI, Groq, or local models.



## 🔮 Roadmap

### v0.1 — Foundations

- KIRI naming & identity
- Package structure
- Swivel & TTS fully integrated
- Wake-up routine
- Behaviour engine skeleton

### v0.2 — Perception & Greetings

- Presence tracking
- Greeting logic
- Return recognition
- Search routine
- Idle motions

### v0.3 — Conversational KIRI

- LLM chat integration
- Listening pose
- Talking pose
- Turn-taking logic

### v0.4 — World Awareness

- OCR
- Object detection
- Context linking
- Memory system

### v0.5 — Emotional Layer (Optional)

- mood based on interactions
- expressive motion variants
- personalization

## 🧙 Author Notes

KIRI is meant to be the smallest possible expression of:

> "A creature that lives with you, not a machine that runs next to you."

It's a robotics experiment in:

- perception
- expression
- personality
- state machines
- human–AI interaction
- tiny magical behaviours

---

## 🛠️ Installing KIRI Core

KIRI requires a Raspberry Pi (4 or 5 recommended), Python 3.10+, and a pan–tilt servo controller.

This guide assumes:

- your Pi is up-to-date
- you are using a virtual environment with `--system-site-packages`
- you want KIRI to run with hardware acceleration, Piper TTS, and YuNet face detection

### 1️⃣ System Prerequisites

Update Raspberry Pi:

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

Install system packages:

```bash
sudo apt install -y \
    python3-venv python3-pip python3-dev \
    libatlas-base-dev libopenblas-dev \
    libjpeg-dev libpng-dev \
    libavcodec58 libavformat58 libswscale5 \
    portaudio19-dev ffmpeg \
    git curl
```

### 2️⃣ Create Virtual Environment

We strongly recommend allowing system packages (for speed and picamera):
DO NOT INSTALL pip picamera!!

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
```

Upgrade tooling:

```bash
pip install --upgrade pip wheel setuptools
```

### 3️⃣ Install OpenCV (headless + contrib)

First remove any leftover OpenCV packages:

```bash
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python-headless || true
```

Install the binary-only contrib build:

```bash
pip install --only-binary=:all: opencv-contrib-python-headless==4.10.0.84
```

Verify:

```bash
python3 - << 'EOF'
import cv2, sys
print("Python:", sys.version.split()[0])
print("OpenCV:", cv2.__version__)
print("FaceDetectorYN:", hasattr(cv2, "FaceDetectorYN"))
print("dnn module:", hasattr(cv2, "dnn"))
EOF
```

You must see:
`FaceDetectorYN: True` and `dnn module: True`.

### 4️⃣ Install KIRI Dependencies

Core libs:

```bash
pip install numpy pyserial onnxruntime
```

Speech:

```bash
pip install piper-tts
```

Optional for chat:

```bash
pip install openai groq
```

### 5️⃣ Download YuNet Face Detector

KIRI uses YuNet for lightweight face detection.

Download:

```bash
mkdir -p assets/models
curl -L \
  -o assets/models/face_detection_yunet_2023mar.onnx \
  https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx
```

### 6️⃣ Install KIRI

In the root of the repo:

```bash
pip install -e .
```

This makes the entire kiri package importable everywhere:

```python
from kiri.modules.tts import TTS
from kiri.modules.swivel import SwivelController
```

### 7️⃣ Verify Hardware

**✔ Camera**

```bash
libcamera-still -o test.jpg
```

**✔ Servo Controller**

```python
python3 - << 'EOF'
from kiri.modules.swivel import SwivelController
sw = SwivelController().open()
sw.center()
EOF
```

The head should move to 90°/90°.

### 8️⃣ Configure Bluetooth Speaker (Optional)

List sinks:

```bash
pactl list short sinks
```

Set default:

```bash
pactl set-default-sink bluez_output.YOUR_DEVICE
```

Verify:

```bash
pactl info | grep "Default Sink"
```

### 9️⃣ Test Piper TTS

```python
python3 - << 'EOF'
from kiri.modules.tts import TTS
tts = TTS()
tts.say("KIRI is ready.")
EOF
```

If it speaks — everything works.

### 🔟 Test KIRI Wake-Up Routine

```bash
python3 scripts/test_wakeup.py
```

You should see:

- center
- twitch
- nod
- scan
- greet

## 🎉 Installation Complete

Now KIRI is alive.
You officially have a tiny mythological house spirit living in your Raspberry Pi.

