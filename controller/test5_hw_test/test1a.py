# Make sure all three buttons are working
from machine import Pin
import pycom
import time

pycom.heartbeat(False)

pycom.rgbled(0xFF0000)  # Red
print("Test1a internal Button monitor 0.5 2018-08-29")

class StateContext:
    def __init__(self):
        print('Stub init')

    def run(self):  # Take any actions or change state
        print('Stub run')

class Heartbeat(StateContext):
    def __init__(self):
        self.count = 0
        self.led = Pin('P9', mode=Pin.OUT)

    def run(self):
        if self.count < 0:
            self.count = 20
            self.led.toggle()
        self.count -= 1

heartbeat = Heartbeat()

keep_running = 200

class Button:
    def __init__(self):
        self.button = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)

    def run(self):
        global keep_running
        if self.button() == 0:  # button pushed
            print('Button pushed stopping')
            keep_running = -1
            pycom.rgbled(0xFF8000)  # Orange

expansion_button = Button()

pycom.rgbled(0x00FF00)  # Green

keep_running = 200
while keep_running > 0:  # Run main loop ca every 0.1 seconds
    expansion_button.run()
    heartbeat.run()
    time.sleep_ms(100)
    keep_running -= 1
pycom.rgbled(0x030101)  # Pale pink
print('Test finished')
