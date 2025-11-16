import asyncio

class BehaviourManager:
    def __init__(self, bus, swivel, tts):
        self.bus = bus
        self.swivel = swivel
        self.tts = tts
        self.current = None
        self.last_name = None
        self.cooldown = 0

        bus.subscribe("face.detected", self.on_face)
        bus.subscribe("face.lost", self.on_loss)

        bus.subscribe("speak", self.on_speak)

    async def on_speak(self, text):
        await self.audio.say(text)


    async def on_face(self, data):
        name = data.get("name")
        box = data.get("box")

        # greet logic
        if name and name != self.last_name and self.cooldown <= 0:
            self.tts.say(f"Hello {name}")
            self.last_name = name
            self.cooldown = 50  # frames or seconds depending on loop

        # swivel tracking
        fx, fy, fw, fh = box
        await asyncio.sleep(0)  # yield
        # (tracking implementation isolated into its own module)
        # swivel_tracker.adjust(box)

    async def on_loss(self, data):
        # after some frames, trigger searching
        pass

    async def tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1
