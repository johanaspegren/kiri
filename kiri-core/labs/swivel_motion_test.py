#!/usr/bin/env python3
import asyncio
import math
from hardware.swivel import SwivelController
from motion.swivel_motion import SwivelMotion


async def test_wave(motion):
    print("Wave left–right")
    for pan in [60, 120, 60, 120, 90]:
        motion.set_target(pan, 90)
        await asyncio.sleep(1.0)


async def test_nod(motion):
    print("Nod up–down")
    for tilt in [70, 110, 70, 110, 90]:
        motion.set_target(90, tilt)
        await asyncio.sleep(1.0)


async def test_curiosity(motion):
    print("Curious tilt")
    # small organic wiggle
    for _ in range(3):
        motion.set_target(110, 80)   # head tilt right
        await asyncio.sleep(0.6)
        motion.set_target(70, 100)   # head tilt left
        await asyncio.sleep(0.6)

    motion.set_target(90, 90)
    await asyncio.sleep(0.8)


async def test_spiral(motion):
    print("Spiral motion")
    # small pan/tilt spiral
    for i in range(60):
        pan  = 90 + 25 * math.sin(i / 8)
        tilt = 90 + 20 * math.cos(i / 8)
        motion.set_target(pan, tilt)
        await asyncio.sleep(0.04)

    motion.set_target(90, 90)
    await asyncio.sleep(1.0)


async def main():
    print("=== Smooth Swivel Motion Test ===")

    sw = SwivelController().open()
    motion = SwivelMotion(sw, hz=30, max_speed=140)

    # Start motion task
    asyncio.create_task(motion.loop())

    await asyncio.sleep(0.5)

    await test_wave(motion)
    await test_nod(motion)
    await test_curiosity(motion)
    await test_spiral(motion)

    print("Resetting to centre…")
    motion.set_target(90, 90)
    await asyncio.sleep(1.0)

    print("Closing…")
    sw.close()

    print("=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())
