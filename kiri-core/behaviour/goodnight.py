import asyncio

async def good_night(bus, swivel):
    # A tiny bow
    swivel.set(90, 110)
    await asyncio.sleep(0.3)

    # Deeper “rest” tilt
    swivel.set(90, 130)
    await asyncio.sleep(0.4)

    # Gentle sway → settling down
    for pan in (88, 92, 90):
        swivel.set(pan, 130)
        await asyncio.sleep(0.25)

    # Speak the farewell
    await bus.publish("speak", "Good night. I am going to sleep now.")
