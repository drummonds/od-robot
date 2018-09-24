# Test MQTT and Async
# 10 second button monitor
from machine import Pin
import pycom
import time
import uasyncio as asyncio

from my_mqtt import MyMqtt

pycom.heartbeat(False)

class RGB:
    def __init__(self):
        self.colour = 0x000000

    def set(self, colour):
        self.colour = colour
        pycom.rgbled(self.colour)

rgb = RGB()

async def killer(duration):
    await asyncio.sleep(duration)

async def toggle(rgbLED, time_ms):
    while True:
        await asyncio.sleep_ms(time_ms)
        colour = rgb.colour
        colour = (colour + 1) % 0xFFFFFF
        rgb.set(colour)  # Purple

# Starting to link to actual outputs to Sensors and multi threaded
# 1 second delays to prevent overloading MQTT which will then fail

rgb.set(0x200000)  # Red
print("test4 version 0.10 2018-08-22")
mq = MyMqtt()
mq.send_value("0", "button")
rgb.set(0x002000)  # Green

async def button_monitor():
    p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
    while True:
        # Button not pushed
        pycom.rgbled(0xFF8000)  # Orange
        mq.send_value("0", "button")
        await asyncio.sleep_ms(1000)
        while p_in() == 1: # Wait for button push
            await asyncio.sleep_ms(100)
        rgb.set(0x008000)  # Green
        mq.send_value("0", "button")
        await asyncio.sleep_ms(1000)
        mq.send_value("1", "button")
        await asyncio.sleep_ms(1000)
        while p_in() == 0: # Wait for button release
            await asyncio.sleep_ms(100)
        rgb.set(0x808000)  # Yellow
        mq.send_value("1", "button")
        await asyncio.sleep_ms(1000)

def test(duration):
    loop = asyncio.get_event_loop()
    duration = int(duration)
    if duration > 0:
        print("Run test for {:3d} seconds".format(duration))
    loop.create_task(toggle(pycom.rgbled, 10))
    loop.create_task(button_monitor())
    loop.run_until_complete(killer(duration))
    loop.close()

test(20)
time.sleep_ms(1000)  # Make sure don't over load sending of data
mq.send_value("0", "button")
rgb.set(0x201010)  # pale pink
print("Test completed")
