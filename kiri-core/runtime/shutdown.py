import asyncio

async def graceful_shutdown(bus, audio, swivel):
    print("[shutdown] draining audio queue…")
    await bus.publish("speak", "Shutting down.")
    
    # give audio queue a moment to accept the message
    await asyncio.sleep(0.1)

    # Wait for all queued speech to finish
    await audio.queue.join()

    # Final goodnight gesture
    swivel.set(90, 140)
    await asyncio.sleep(0.4)
    swivel.center()

    print("[shutdown] complete")
