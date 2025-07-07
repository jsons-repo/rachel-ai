# src/rachel/api/pubsub.py

import asyncio

subscribers: set[asyncio.Queue] = set()

def subscribe() -> asyncio.Queue:
    q = asyncio.Queue(maxsize=100)
    subscribers.add(q)
    return q

def unsubscribe(q: asyncio.Queue):
    subscribers.discard(q)

def broadcast_to_all_clients(data):
    for q in list(subscribers):
        try:
            q.put_nowait(data)
        except asyncio.QueueFull:
            # Optional: remove slow client queues
            subscribers.discard(q)
