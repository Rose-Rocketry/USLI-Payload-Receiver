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

from pickle import UnpicklingError
import pickle
import serial
import websockets
import asyncio
import concurrent.futures

ser = serial.Serial('/dev/ttyUSB0', baudrate=115200,timeout=0.5)
messages_received = 0

async def process_packets(socket):
    while True:
        buf = bytearray(0)
        while b'.STOPSTOPSTOPSTOP' not in buf[-17:]:
            buf.append(ser.read())

        try:
            data = pickle.loads(buf)
            await socket.send({"status":"successful","id":messages_received,"data":data})
        except UnpicklingError:
            {"status":"packet lost", "id": messages_received}
        messages_received += 1

async def main():
    async for socket in websockets.connect("ws://localhost:8000/ws/telemetry/PiLoad/send"):
        try:
            await process_packets( socket)
        except websockets.ConnectionClosed:
            #automatically reconnects
            continue
