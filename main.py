"""
Refereneces:
Async Serial: https://tinkering.xyz/async-serial/
PySerial Doc: https://pyserial-asyncio.readthedocs.io/en/latest/shortintro.html
Asyncio Docs:
 - Low Level API: https://docs.python.org/3/library/asyncio-llapi-index.html
 - Queues: https://docs.python.org/3/library/asyncio-queue.html#asyncio.Queue
 - Transports: https://docs.python.org/3/library/asyncio-protocol.html#base-transport

Websockets: https://websockets.readthedocs.io/en/stable/reference/client.html

"""

import asyncio
from functools import partial
import serial_asyncio
import pickle
import json
import websockets

class ReaderProtocol(asyncio.Protocol):

    def __init__(self, queue):
        super.__init__()
        self.transport = None
        self.queue = queue

    """Stores serial data and prepares it to recieve"""
    def connection_made(self, transport):
        self.transport = transport
        self.buf = bytes()
        self.msgs_received = 0

    async def data_received(self, data: bytes):
        """Stores received data until we receive a `.`"""
        self.buf += data
        if b'.' in self.buf:
            pickles = self.buf.split(b'.')
            for message in pickles[:-1]:
                # Decode Message
                depickle = pickle.loads(message)
                #Send message to queue
                asyncio.ensure_future(self.queue.put(depickle))

async def queue_messenger(websocket, queue):
    while True:
        next_message = await queue.get()
        data = json.dumps(next_message)
        websocket.send(data)

async def main():
    #Get event loop
    loop = asyncio.get_running_loop()

    #Set up queue
    queue = asyncio.Queue()
    reader = partial(ReaderProtocol, queue)

    #Create serial connection
    coro = await serial_asyncio.create_serial_connection(loop, reader, '/dev/ttyS0', baudrate=115200)

    trasnport, protocol = loop.run_until_complete(coro)
    async for websocket in websockets.connnect("ws://127.0.0.1:8000/ws/telemetry/PiLoad/send",open_timeout = None):
        try:
            queue_messenger(websocket, queue)
        except websockets.ConnectionClosed:
            continue

asyncio.run(main())