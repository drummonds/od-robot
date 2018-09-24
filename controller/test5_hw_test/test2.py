# Test4 trying to ramp rotor
from machine import Pin
import pycom
import time
from machine import PWM

# initialisation code
pycom.heartbeat(False)
pycom.rgbled(0x008080)  # Start colour

class Button:
    def __init__(self):
        self.state = 0
        # make `P10` an input with the pull-up enabled
        self.p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
        self.pushed = False

    def run(self):
        if self.state == 0:  # Waiting for button push
            if self.p_in() == 1:
                self.pushed = True  # For one duty_cycle
                self.state = 1
        elif self.state == 1:  # Waiting for button release
            self.pushed = False  # Cancel button push true for one cycle only
            if self.p_in() == 0:
                self.state = 0
        else:
            self.state = 0

btn = Button()

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

# initialize `P9` in gpio mode and make it an output
p_out = Pin('P9', mode=Pin.OUT)
p_out.value(1)
p_out.value(0)
p_out.toggle()
p_out(True)


# Program loop
running = True
while running:
    th.run()
    btn.run()
    p_out.toggle()
    time.sleep(0.5)
