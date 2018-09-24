# clean.py Test of asynchronous mqtt client with clean session.
# (C) Copyright Peter Hinch 2017.
# Released under the MIT licence.
# Modified for Pycom board in an expansion board


# The use of clean_session means that after a connection failure subscriptions
# must be renewed (MQTT spec 3.1.2.4). This is done by the connect handler.
# Note that publications issued during the outage will be missed. If this is
# an issue see unclean.py.

# red LED: ON == WiFi fail
# blue LED heartbeat: demonstrates scheduler is running.

# from mqtt_as import MQTTClient
from config import config
import pycom
import uasyncio as asyncio
from machine import Pin

print("MyMqtt Clean test1 V0.1 2018-08-29")

pycom.heartbeat(False)

class RGB:
    def __init__(self):
        self.colour = 0x000000

    def set(self, colour):
        self.colour = colour
        pycom.rgbled(self.colour)

rgb = RGB()


with open("secret.json", "r") as f:
    secrets = ujson.load(f)


# Subscription callback
def sub_cb(topic, msg):
    print((topic, msg))

# Demonstrate scheduler is operational.
async def heartbeat():
    led = Pin('P9', mode=Pin.OUT)  # LED on Expansion board
    while True:
        await asyncio.sleep_ms(500)
        led(not led())

#wifi_led = Pin(0, Pin.OUT, value=0)  # LED on for WiFi fail/not ready yet

async def wifi_han(state):
    if state:
        rgb.set(0x002000)  # Green
    else:
        rgb.set(0x200000)  # Red
    wifi_led(state)
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('foo_topic', 1)

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        return
    n = 0
    while True:
        await asyncio.sleep(5)
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        await client.publish('result', '{} {}'.format(n, client.REPUB_COUNT), qos = 1)
        n += 1

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True
config['server'] = secrets['MQTT_SERVER']
config['user'] = secrets['MQTT_USER']
config['password'] = secrets['MQTT_PASSWORD']

# Set up client
##MQTTClient.DEBUG = True  # Optional
##client = MQTTClient(config)
client = None

loop = asyncio.get_event_loop()
loop.create_task(heartbeat())
try:
    loop.run_until_complete(main(client))
finally:
    pass
    ##client.close()  # Prevent LmacRxBlk:1 errors
