import asyncio

async def wake_up(bus, swivel):
    # Soft lift + slight “hello” nod
    swivel.set(90, 120)    # tilt up
    await asyncio.sleep(0.4)
    swivel.set(90, 80)     # tilt down
    await asyncio.sleep(0.2)
    swivel.set(90, 100)    # neutral
    await asyncio.sleep(0.3)
    # Small side-to-side “curious wiggle”
    await bus.publish("speak", "Good morning. I am awake and operational.")
    for pan in (70, 110, 90):
        swivel.set(pan, 100)
        await asyncio.sleep(0.25)
    print("[wake] completed")
