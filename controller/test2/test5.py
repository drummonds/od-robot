# Starting to link to actual outputs to Sensors and multi threaded
import _thread
from machine import Pin
import pycom
import time

from my_mqtt import MyMqtt

VERSION = '0.1.5 2018-08-20'
# Getting read for first version

pycom.heartbeat(False)

pycom.rgbled(0xFF0000)  # Red
print("Hi {}".format(VERSION))
mq = MyMqtt()
mq.send_value("1", "button")
pycom.rgbled(0x00FF00)  # Green

def button_monitor():
    p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
    while True:
        # Button not pushed
        pycom.rgbled(0xFF8000)  # Orange
        mq.send_value("0", "button")
        while p_in() == 0: # Wait for button push
            pycom.rgbled(0x008000)  # Green
            time.sleep(0.1)
        mq.send_value("1", "button")
        while p_in() == 1: # Wait for button release
            pycom.rgbled(0x008080)  # Cyan
            time.sleep(0.1)

_thread.start_new_thread(button_monitor, ())

# Needs to be reset
while True:
    time.sleep(1)
