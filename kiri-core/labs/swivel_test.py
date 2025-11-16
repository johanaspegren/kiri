import asyncio
from hardware.swivel import SwivelController


async def run():
    with SwivelController().open() as sw:
        print("KIRI waking...")
        sw.center()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(run())
