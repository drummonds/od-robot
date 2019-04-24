import pycom
import time

from machine import Pin
from time import sleep_us

class Stepper():
    def __init__(self, pin_a, pin_b, pin_c, pin_d,):
        self.pins = []
        for pin in (pin_a, pin_b, pin_c, pin_d):
            self.pins.append(Pin(pin, mode=Pin.OUT))
        self.stop()

    def stop(self):
        for pin in self.pins:
            pin.value(0)

    def cycle(self):
        self.stop()
        for pin in self.pins:
            pin.value(1)
            time.sleep(1)
            pin.value(0)
        time.sleep(1)
        self.stop()

print('Hello V0.5')

pycom.heartbeat(False)

stepper1 = Stepper('P23', 'P22', 'P21', 'P20')

for i in range(1):
    pycom.rgbled(0xFF0000)  # Red
    stepper1.pins[0].value(1)
    time.sleep(1)
    pycom.rgbled(0x00FF00)  # Green
    stepper1.pins[1].value(1)
    time.sleep(1)
    pycom.rgbled(0x0000FF)  # Blue
    stepper1.pins[0].value(0)
    stepper1.pins[0].value(0)
    stepper1.pins[2].value(1)
    time.sleep(1)

stepper1.stop()
stepper1.cycle()
stepper1.pins[2].value(1)
stepper1.pins[3].value(0)
pycom.rgbled(0x002020)  # Blue
