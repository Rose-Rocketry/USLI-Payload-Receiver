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
import json
import serial
import websockets
import asyncio
import concurrent.futures
import logging

ser = serial.Serial('/dev/ttyUSB0', baudrate=115200,timeout=0.5)

async def process_packets(socket):
    print("Looping")
    while True:
        packet = None
        buf = bytes()
        while b'.STOPSTOPSTOPSTOP' not in buf[-17:] :
            item = ser.read()
            if b'' == item:
                continue
            buf += item

        print(len(buf))
        print(buf)
        try:
            print("Data")
            data = pickle.loads(buf[:-16])
            logging.info("Recieved Packet")
            await socket.send(json.dumps({"status":"successful","data":data}))
            print("succ")
        except UnpicklingError as e:
            logging.info("Failed to read packet")
            await socket.send(json.dumps({"status":"packet lost", "error":str(e)}))
        except Exception as e:
            logging.info("Failed to read packet")
            print
            await socket.send(json.dumps({"status":"packet lost", "error":str(e)}))
        await asyncio.sleep(0)

async def main():
    async for socket in websockets.connect("ws://localhost:8000/ws/telemetry/PiLoad/send"):
        try:
            await process_packets(socket)
        except websockets.ConnectionClosed:
            #automatically reconnects
            logging.warning("Could not connect to websocket.")
            print("failed")
            continue

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
