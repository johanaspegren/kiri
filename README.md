
🐾 KIRI — A Tiny Curious Companion Powered by KIRI Core

A small embodied AI creature running on Raspberry Pi 5 with an IMX500 neural camera, expressive motion, and a very small attention span.

🌟 Overview

KIRI is a micro-robotic creature built to feel curious, perceptive, and alive.
It lives on:

Raspberry Pi 5

IMX500 neural imaging sensor

Pan–tilt head with Arduino servo driver

Local TTS (Piper)

CPU face detection (YuNet)

Behaviour-driven motion

LLM conversational brain (optional)

KIRI is not humanoid.
It is not a cartoon.
It is more like a small house spirit that is mildly surprised to discover you exist.

🧠 KIRI Core — Architecture

KIRI Core is the modular framework behind:

Perception

Motion

Behaviour

Audio

State management

Integrations (LLM, IMX500 detections, etc.)

The architecture is intentionally simple, asynchronous, and fault-tolerant.

🗺️ High-Level Architecture Diagram
                   ┌────────────────────────────────────────┐
                   │                KIRI CORE                │
                   └────────────────────────────────────────┘
                                  ▲               ▲
                 Perception       │               │     Behaviour
                                  │               │
                                  │               │

         ┌──────────────────────┐ │   ┌──────────────────────────────┐
         │   Picamera2 (RGB)    │ │   │        Behaviour Loops        │
         │  640×480 stable feed │ │   │  - TrackFace                  │
         └──────────────────────┘ │   │  - WakeUp / Sleep             │
                 │                │   │  - CuriousScan                │
     CPU Face Detection (YuNet)   │   └──────────────────────────────┘
                 │                │                │
                 ▼                │                ▼

       ┌───────────────────┐      │     ┌────────────────────────┐
       │  FACE REFINER     │──────┘     │     SwivelMotion        │
       └───────────────────┘            │ (smooth servo control)  │
                 │                      └────────────────────────┘
                 ▼                                │
        Shared State (frame + faces)              ▼
                 │                      ┌──────────────────────┐
                 │                      │  SwivelController    │
                 │                      │ (Arduino servo board)│
                 │                      └──────────────────────┘
                 ▼
      ┌────────────────────────┐
      │    IMX500 Detector     │
      │ (neural metadata only) │
      └────────────────────────┘
                 │
      Object detection, cues,
     ambient awareness (future)

📸 Camera Architecture — Why It Works This Way

This part is crucial for stability and future-proofing.

✔ 1. Picamera2 provides ALL imaging

YuNet (face detector) needs:

Correct RGB

Predictable resolution

No overlays

No aspect-ratio trickery

Using IMX500 frames for CPU vision results in:

lag

bounding-box drift

servo “tornado mode”

IMX firmware upload stalls

general emotional distress

Therefore:
All OpenCV-based detection uses Picamera2 at 640×480 RGB.

This gives perfectly stable geometry → perfectly stable tracking.

✔ 2. IMX500 is used for neural inference ONLY

The IMX500 is not a camera.
It is a camera-shaped neural chip.

We use it only for:

onboard object detection

low-CPU awareness

future cues (person, pet, object, light, “presence”)

We never use its RGB output.

This matches Sony’s reference design and avoids:

DMA contention

allocator crashes

double-stream conflicts

Raspberry Pi kernel panics (the fun kind)

✔ 3. Behaviour and motion depend on stable perception

Servo behaviour only works when fed:

stable bounding boxes

consistent timing

clean frames

By separating IMX500 metadata from Picamera2 imaging:

tracking stops oscillating

gaze stabilises

KIRI behaves like a creature instead of an industrial fan

✔ 4. This design is modular and future-safe

Because the camera and detection systems are disentangled:

You can add gesture recognition

or IMX-based “curiosity triggers”

or person recognition

or ambient detection

or LLM multimodal reasoning

without rewriting the core.

🧱 Project Structure
kiri-core/
│
├── hardware/
│   ├── swivel.py             # Arduino servo interface
│   ├── imx500_detector.py    # Neural inference module
│
├── motion/
│   └── swivel_motion.py      # Smooth, async servo control
│
├── perception/
│   ├── face_refiner.py       # YuNet face detector
│   ├── face_provider.py      # Best-face selection
│   └── preview.py            # Local or web visualisation
│
├── behaviour/
│   ├── track_face.py         # Gaze tracking behaviour
│   └── wakeup.py             # Waking ritual
│
├── runtime/
│   ├── event_bus.py          # Publish/subscribe system
│   ├── audio_manager.py      # Piper TTS
│   ├── web_preview.py        # JPEG streaming server
│
└── config/
    └── models.py             # Paths to YuNet/embedders/etc.

🏃‍♂️ Running the System
Minimal test:
python labs/face_detect_test.py

Full creature mode:
python labs/test_face_tracker.py


Once running:

See live preview at
http://raspberrypi.local:8080

KIRI will track your face

Servo motion is smooth

IMX500 draws detection boxes

YuNet feeds the behaviour system

🔮 Future Additions (fully supported by this architecture)

IMX500-based ambient curiosity detection

“Look-at-sound” microphone localisation

Emotional micro-movements (breathing, twitching)

LLM-based attention redirection

Person recognition + friendly greetings

Object-of-interest tracking

Scene curiosity scoring

KIRI is tiny, but the roadmap is not.

📜 Why This Architecture Wins

Stable

Predictable

Expandable

Uses IMX500 as intended

Keeps high-frequency control loops responsive

Avoids frame format hell

Fully asynchronous

Behaviour-driven (creature-like)

Most importantly:

It prevents KIRI from spinning wildly while claiming confidently that your face is “somewhere behind the radiator.”





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

