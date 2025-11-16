import asyncio
from runtime.event_bus import EventBus
from runtime.audio_manager import AudioManager
from runtime.shutdown import graceful_shutdown
from hardware.swivel import SwivelController

from behaviour.wakeup import wake_up
from behaviour.goodnight import good_night

async def main():
    bus = EventBus()

    # Start audio subsystem
    audio = AudioManager()
    await audio.start()
    bus.subscribe("speak", audio.say)

    with SwivelController().open() as swivel:

        # Wake up KIRI
        await wake_up(bus, swivel)

        # Say something after waking up
        await bus.publish("speak", "System online and ready.")
        await asyncio.sleep(2.0)

        # Good night routine BEFORE shutting down runtime
        await good_night(bus, swivel)

        # Graceful shutdown: drain speech + center servo
        await graceful_shutdown(bus, audio, swivel)


if __name__ == "__main__":
    asyncio.run(main())
