# Make sure all three buttons are working
from machine import Pin, PWM
import pycom
import time

from rotate_axis import Rotate
from z_axis import ZAxis

pycom.heartbeat(False)

pycom.rgbled(0xFF0000)  # Red
print("OD Robot Controller 1.12 2018-09-26")

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
        self.is_active = False
        self.button_up = Pin('G4', mode=Pin.IN, pull=Pin.PULL_UP)
        self.button_dwn = Pin('G5', mode=Pin.IN, pull=Pin.PULL_UP)

    def activate(self):
        # May not be switched on
        if not self.is_active:
            self.is_active = True
            self.pwm_c = self.pwm.channel(0, pin='P12', duty_cycle=0.15)

    def set_position(self, position): # Converts to 1 -2 ms pulses
        self.activate()
        # speed in %
        dc = (position / 100.0) * (1/20) + (1/20)
        self.pwm_c.duty_cycle(dc)
        return dc

    def park(self):
        self.set_position(50)

    def grip(self):
        self.set_position(0)

    def release(self):
        self.set_position(100)

    def shutdown(self):
        # Ideally won't move servo
        self.pwm_off = Pin('P12', mode=Pin.IN, pull=Pin.PULL_UP)
        self.is_active = False


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

    def state_text(self):
        if th.is_active:
            return "Active, pos {}".format(self.position)
        else:
            return "Off, last pos {}".format(self.position)

z_axis = ZAxis(th.pwm)
rotate = Rotate(th.pwm)

pwm = PWM_Controller()

def status():
    print('Toolhead at {}. Zaxis is {}'.format(pwm.state_text(),
        z_axis.state_text()))

def load():
    th.release()
    z_axis.nudge(50, run_time=100)
    th.grip()
    z_axis.nudge(44, run_time=100)

def release():
    # Assume at top
    z_axis.nudge(50, run_time=20)
    th.release()
    time.sleep_ms(100)  # wait for DVD to be unloaded
    th.park()
    th.shutdown()
    z_axis.nudge(44, run_time=30)


pycom.rgbled(0x103000)  # Pale Green
th.park()
print('Test finished')
