# Make sure all three buttons are working
from machine import Pin, PWM
import pycom
import time

pycom.heartbeat(False)

pycom.rgbled(0xFF0000)  # Red
print("Test3 internal Button monitor 0.8 2018-08-29")

class Heartbeat:
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


class ToolHead:

    def __init__(self):
        # create pwm channel on pin P12
        self.pwm = PWM(0, frequency=50)  # use PWM timer 0, with a frequency of 50Hz
        self.pwm_c = self.pwm.channel(0, pin='P12', duty_cycle=0.15)
        self.state = 0

    def set_position(self, position): # Converts to 1 -2 ms pulses
        # speed in %
        dc = (position / 100.0) * (1/20) + (1/20)
        self.pwm_c.duty_cycle(dc)
        return dc

    def park(self):
        self.set_position(50)

    def grip(self):
        self.set_position(100)

    def release(self):
        self.set_position(0)

    def run(self):
        global running, btn
        if self.state == 0:
            pycom.rgbled(0x002000)
            self.state = 1
            self.park()
        elif self.state == 1:
            pycom.rgbled(0x008000)
            if btn.pushed:
                self.state = 2
                self.release()
        elif self.state == 2:
            pycom.rgbled(0x000080)
            if btn.pushed:
                self.state = 3
                self.grip()
        elif self.state == 3:
            pycom.rgbled(0x808000)
            if btn.pushed:
                self.state = 4
                self.release()
        else:
            self.state == 4
            pycom.rgbled(0x200000)
            if btn.pushed:
                running = False
                self.park()
                pycom.rgbled(0x800000)

th = ToolHead()
th.park()

class PWM_Controller:
    def __init__(self):
        self.button_up = Pin('G4', mode=Pin.IN, pull=Pin.PULL_UP)
        self.button_dwn = Pin('G5', mode=Pin.IN, pull=Pin.PULL_UP)
        self.position = 50

    def run(self):
        action = False
        if self.button_up() == 0:  # button pushed
            action = True
            if self.position < 100:
                self.position = self.position + 1
        elif self.button_dwn() == 0:  # button pushed
            action = True
            if self.position > 0:
                self.position = self.position - 1
        if action:
            if self.position % 10 == 0:
                print("PWM = {}".format(self.position))
            th.set_position(self.position)
            pycom.rgbled(int(self.position * 255 / 100))  # Shade of blue

pwm = PWM_Controller()
pycom.rgbled(0x00FF00)  # Green

keep_running = 300
while keep_running > 0:  # Run main loop ca every 0.1 seconds
    expansion_button.run()
    heartbeat.run()
    pwm.run()
    time.sleep_ms(100)
    keep_running -= 1
pycom.rgbled(0x030101)  # Pale pink
th.park()
print('Test finished')
