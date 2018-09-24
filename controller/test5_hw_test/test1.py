# Very simple program that replicates button to RGB rgbled
# Runs indefinitely, can be reset
from machine import Pin
import pycom
import time

pycom.heartbeat(False)

pycom.rgbled(0xFF0000)  # Red
print("Test1 internal Button monitor '0.1 2018-08-29'")

def button_monitor():
    p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
    while True:
        # Button not pushed
        pycom.rgbled(0xFF8000)  # Orange
        while p_in() == 0: # Wait for button push
            pycom.rgbled(0x008000)  # Green
            time.sleep(0.1)
        while p_in() == 1: # Wait for button release
            pycom.rgbled(0x008080)  # Cyan
            time.sleep(0.1)

pycom.rgbled(0x00FF00)  # Green

# Needs to be reset
button_monitor()
