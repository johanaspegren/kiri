#!/usr/bin/env python3
import asyncio
from hardware.swivel import SwivelController

async def run():
    print("=== Swivel Test Start ===")

    # Open controller outside of 'with', because we want async flexibility
    sw = SwivelController().open()

    try:
        print("Moving: pan -30°")
        sw.pan(-30)
        await asyncio.sleep(0.4)

        print("Moving: pan +30°")
        sw.pan(30)
        await asyncio.sleep(0.4)

        print("Moving: tilt -30°")
        sw.tilt(-30)
        await asyncio.sleep(0.4)

        print("Moving: tilt +30°")
        sw.tilt(30)
        await asyncio.sleep(0.4)

        print("Absolute set: 90/90")
        sw.set(90, 90)
        await asyncio.sleep(0.4)

        print("Absolute set: 60/60")
        sw.set(60, 60)
        await asyncio.sleep(0.4)

        print("Absolute set: 120/120")
        sw.set(120, 120)
        await asyncio.sleep(0.4)

        print("Reset centre")
        sw.set(90, 90)
        await asyncio.sleep(0.4)

    finally:
        print("Closing swivel controller.")
        sw.close()

    print("=== Swivel Test Complete ===")

if __name__ == "__main__":
    asyncio.run(run())
