# swivel.py
from __future__ import annotations
import time, sys, os
from pathlib import Path
from typing import Optional

try:
    import serial
    from serial.tools import list_ports
except ImportError as e:
    raise RuntimeError("pyserial not installed. Run: pip install pyserial") from e

DEFAULT_BAUD = 9600

def _find_port(preferred: Optional[str] = None) -> Optional[str]:
    if preferred:
        return preferred
    # Stable path on Linux (Raspberry Pi)
    by_id = Path("/dev/serial/by-id")
    if by_id.exists():
        ids = sorted(p for p in by_id.iterdir() if p.is_symlink())
        if ids:
            return str(ids[0])
    # Fallbacks (Linux & Windows)
    for cand in ("/dev/ttyACM0", "/dev/ttyUSB0"):
        if Path(cand).exists():
            return cand
    # Windows: pick something Arduino-ish
    ports = list(list_ports.comports())
    for p in ports:
        d = (p.description or "").lower()
        if any(k in d for k in ("arduino", "ch340", "cp210", "usb serial")):
            return p.device
    return ports[0].device if ports else None

class SwivelController:
    """Tiny client for the Arduino pan/tilt (S/P/T/C protocol)."""
    def __init__(self, port: Optional[str] = None, baud: int = DEFAULT_BAUD, reset_wait_s: float = 2.0):
        self.port = _find_port(port)
        if not self.port:
            raise RuntimeError("No serial port found. Plug the Arduino in or specify port explicitly.")
        self.baud = baud
        self._ser: Optional[serial.Serial] = None
        self._reset_wait_s = reset_wait_s

    # --- context manager sugar ---
    def __enter__(self) -> "SwivelController":
        return self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # --- lifecycle ---
    def open(self) -> "SwivelController":
        if self._ser is None:
            self._ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(self._reset_wait_s)  # give Arduino time to reset
            self._ser.reset_input_buffer()
        return self

    def close(self):
        if self._ser:
            try:
                self._ser.close()
            finally:
                self._ser = None

    # --- low-level send ---
    def _send(self, line: str) -> str:
        if not self._ser:
            raise RuntimeError("Serial not open. Use .open().")

        # Send immediately
        self._ser.write((line.strip() + "\n").encode("ascii"))

        # Non-blocking read (timeout=0 means return instantly)
        self._ser.timeout = 0
        resp = self._ser.readline().decode(errors="ignore").strip()

        return resp

    # --- high-level API ---
    def set(self, pan: int, tilt: int) -> str:
        """Absolute angles in degrees (0–180, clamped by Arduino)."""
        return self._send(f"S {int(tilt)} {int(pan)}")

    def pan(self, delta: int) -> str:
        """Relative pan delta in degrees (±)."""
        return self._send(f"T {int(delta)}")

    def tilt(self, delta: int) -> str:
        """Relative tilt delta in degrees (±)."""
        return self._send(f"P {int(delta)}")

    def cfg(self, vel_deg_s: float, acc_deg_s2: float) -> str:
        """Configure smoothing on the Arduino (V/A)."""
        return self._send(f"C V {float(vel_deg_s)} A {float(acc_deg_s2)}")

    def center(self) -> str:
        return self.set(90, 90)

# --- optional: tiny CLI ---
def _main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Arduino pan/tilt swivel controller")
    ap.add_argument("--port", help="Serial port (e.g., /dev/serial/by-id/usb-… or COM7)")
    ap.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("set", help="Absolute: S <pan> <tilt>")
    s.add_argument("pan", type=int)
    s.add_argument("tilt", type=int)

    p = sub.add_parser("pan", help="Relative: P <delta>")
    p.add_argument("delta", type=int)

    t = sub.add_parser("tilt", help="Relative: T <delta>")
    t.add_argument("delta", type=int)

    c = sub.add_parser("cfg", help="Config smoothing: C V <vel> A <acc>")
    c.add_argument("vel", type=float)
    c.add_argument("acc", type=float)

    sub.add_parser("center", help="S 90 90")

    args = ap.parse_args(argv)
    with SwivelController(port=args.port, baud=args.baud) as sw:
        if args.cmd == "set":
            print(sw.set(args.pan, args.tilt))
        elif args.cmd == "pan":
            print(sw.pan(args.delta))
        elif args.cmd == "tilt":
            print(sw.tilt(args.delta))
        elif args.cmd == "cfg":
            print(sw.cfg(args.vel, args.acc))
        elif args.cmd == "center":
            print(sw.center())

if __name__ == "__main__":
    _main()
