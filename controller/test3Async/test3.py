# aledflash.py Demo/test program for MicroPython asyncio
# Author: Peter Hinch
# Copyright Peter Hinch 2017 Released under the MIT license
# Flashes the onboard LED's each at a different rate. Stops after ten seconds.
# Run on MicroPython board bare hardware

import pycom

pycom.heartbeat(False)

import uasyncio as asyncio

async def killer(duration):
    await asyncio.sleep(duration)

async def toggle(rgbLED, time_ms):
    colour = 0x0
    while True:
        await asyncio.sleep_ms(time_ms)
        rgbLED(colour)  # Purple
        colour = (colour + 1) % 0xFFFFFF

def test(duration):
    print("test3 version 0.2 2018-08-21")
    loop = asyncio.get_event_loop()
    duration = int(duration)
    if duration > 0:
        print("Flash LED's for {:3d} seconds".format(duration))
    loop.create_task(toggle(pycom.rgbled, 10))
    loop.run_until_complete(killer(duration))
    loop.close()

test(10)
