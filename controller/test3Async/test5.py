# Test MQTT and Async
# 10 second button monitor
# From test4 adding a wrapper for MQTT so that only sends data rate limited
from machine import Pin
import pycom
import time
import uasyncio as asyncio

import my_mqtt

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
print("test5 version 0.22 2018-08-23")
mq = my_mqtt.MyMqtt()
rgb.set(0x002000)  # Green

async def flash_onboard():
    # initialize `P9` in gpio mode and make it an output
    p_out = Pin('P9', mode=Pin.OUT)
    while True:
        p_out.toggle()
        await asyncio.sleep_ms(1000)

class MQTTLimited:
    def __init__(self):
        self.queue = []

    def send_value(self, value, feed):
        self.queue.append([value, feed])

my_mq = MQTTLimited()

async def mq_queue():
    delay = 500
    while True:
        if len(my_mq.queue) > 0:
            item = my_mq.queue.pop(0)
            value = item[0]
            feed = item[1]
            count = 0
            print('Sending {}, {}'.format(feed, value))
            while count < 3:
                try:
                    mq.send_value(value, feed)
                    break
                except OSError as e:
                    print('OSError repeat on send message count = {}, {}'.format(
                        count, e))
                    count +=1
                await asyncio.sleep_ms(delay)  # Rate limiter
            if count >=3:
                print('OSError fail on send message')
                raise e
        await asyncio.sleep_ms(delay)  # Rate limiter
        mq.poll()


async def button_monitor():
    p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
    while True:
        # Button not pushed
        pycom.rgbled(0xFF8000)  # Orange
        my_mq.send_value("0.1", "button")
        while p_in() == 1: # Wait for button push
            await asyncio.sleep_ms(100)
        rgb.set(0x008000)  # Green
        my_mq.send_value("0", "button")
        my_mq.send_value("1", "button")
        while p_in() == 0: # Wait for button release
            await asyncio.sleep_ms(100)
        rgb.set(0x808000)  # Yellow
        my_mq.send_value("0.9", "button")

def test(duration):
    loop = asyncio.get_event_loop()
    duration = int(duration)
    if duration > 0:
        print("Run test for {:3d} seconds".format(duration))
    loop.create_task(toggle(pycom.rgbled, 10))
    loop.create_task(button_monitor())
    loop.create_task(flash_onboard())
    loop.create_task(mq_queue())
    loop.run_until_complete(killer(duration))
    loop.close()

def main(duration=60):
    test(duration)
    time.sleep_ms(1000)  # Make sure don't over load sending of data
    # mq.send_value("0", "button")  # Send not queued as event queue halted
    rgb.set(0x201010)  # pale pink
    print("Test completed")

main()
