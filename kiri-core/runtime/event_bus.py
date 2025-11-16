import asyncio
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event, callback):
        self.subscribers[event].append(callback)

    async def publish(self, event, data=None):
        for cb in self.subscribers[event]:
            asyncio.create_task(cb(data))
