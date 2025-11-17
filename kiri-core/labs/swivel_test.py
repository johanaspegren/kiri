import asyncio
from hardware.swivel import SwivelController


async def run():
    with SwivelController().open() as sw:
        print("KIRI waking...")
        sw.pan(-30)
        await asyncio.sleep(0.4)
        sw.pan(30)
        await asyncio.sleep(0.4)

        print("KIRI waking...")
        sw.tilt(-30)
        await asyncio.sleep(0.4)
        sw.tilt(30)
        await asyncio.sleep(0.4)

        print("KIRI waking...")
        sw.set(90, 90)
        await asyncio.sleep(0.4)
        sw.set(60, 60)
        await asyncio.sleep(0.4)
        sw.set(120, 120)
        await asyncio.sleep(0.4)
        sw.set(90, 90)
        await asyncio.sleep(0.4)


    print("Done.")

if __name__ == "__main__":
    asyncio.run(run())
