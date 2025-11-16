# modules/piper_tts.py
from pathlib import Path
import os
import re
import wave
import subprocess
from piper.voice import PiperVoice  # pip install piper-tts


# ---- config / defaults ----
PROJECT = Path(__file__).resolve().parents[1]
VOICE_PATH = Path(os.environ.get("PIPER_VOICE", "/usr/share/piper/voices/en/en_GB-cori-high.onnx"))
CONFIG_PATH = Path(os.environ.get("PIPER_CONFIG", str(VOICE_PATH) + ".json"))
ALSA_DEVICE = os.environ.get("ALSA_DEVICE", "plughw:2,0")

# -------------------------------
# DEVICE DETECTION HELPERS
# -------------------------------

def alsa_usb_available():
    """Return True if ALSA device hw:2,0 exists."""
    try:
        out = subprocess.check_output(["aplay", "-l"]).decode()
        return "card 2:" in out and "device 0:" in out
    except Exception:
        return False

def detect_bluetooth_sink():
    """Return PulseAudio sink name for Bluetooth (or None)."""
    try:
        out = subprocess.check_output(["pactl", "list", "sinks"]).decode()
        # Look for sinks like: Name: bluez_output.XX_XX_XX...
        m = re.search(r"Name:\s*(bluez_output\.[\w\.\-]+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


# ---- internal voice cache ----
_voice = None
def _get_voice():
    global _voice
    if _voice is None:
        if not VOICE_PATH.exists() or not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Piper voice or JSON missing:\n{VOICE_PATH}\n{CONFIG_PATH}")
        _voice = PiperVoice.load(str(VOICE_PATH), config_path=str(CONFIG_PATH))
    return _voice

def _synthesize_wav(text: str, wav_handle):
    v = _get_voice()
    if hasattr(v, "synthesize_wav"):
        v.synthesize_wav(text, wav_handle)
    else:
        v.synthesize(text, wav_handle)

def synthesize_to_file(text: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav:
        _synthesize_wav(text, wav)
    return output_path


# -------------------------------
#  UNIVERSAL PLAYBACK
# -------------------------------
def play(output_path: Path) -> int:
    """
    Intelligent playback:
      1) Use USB ALSA hw:2,0 if available
      2) Otherwise use Bluetooth sink (PulseAudio)
      3) Otherwise fall back to default PulseAudio sink
    """

    # ----------- PRIORITY 1: USB SPEAKER (ALSA hw:2,0) -----------
    if alsa_usb_available():
        cmd = ["aplay", "-q", "-D", "hw:2,0", str(output_path)]
        print("[TTS] Using USB speaker (hw:2,0)")
    else:
        # ----------- PRIORITY 2: BLUETOOTH (PulseAudio/pipewire) -----------
        bt_sink = detect_bluetooth_sink()
        if bt_sink:
            cmd = ["paplay", "--device", bt_sink, str(output_path)]
            print(f"[TTS] Using Bluetooth sink: {bt_sink}")
        else:
            # ----------- PRIORITY 3: SYSTEM DEFAULT SINK -----------
            cmd = ["paplay", str(output_path)]
            print("[TTS] Using default PulseAudio sink")

    # Execute
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout).decode().strip()
        print("[TTS PLAY ERROR]", msg)

    return proc.returncode

# ---- Friendly wrapper ----
class TTS:
    """Simple Piper-based text-to-speech wrapper."""
    def __init__(self, tmp_dir="assets/tts_cache"):
        self.tmp_dir = Path(tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def say(self, text: str, filename: str = None):
        """Generate and play speech."""
        if not text.strip():
            return
        filename = filename or f"tts_{abs(hash(text)) % (10**8)}.wav"
        path = self.tmp_dir / filename
        synthesize_to_file(text, path)
        play(path)

# ---- Handy CLI ----
if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello. Piper minimal test."
    out  = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("assets/tts_test.wav")
    synthesize_to_file(text, out)
    print("Wrote:", out, "size:", out.stat().st_size, "bytes")
    play(out)
