# Test4 trying to ramp rotor
from machine import Pin
import pycom
import time
from machine import PWM

# initialisation code
pycom.heartbeat(False)
pycom.rgbled(0x008080)  # Start colour


def speed_to_dc(speed): # Converts to 1 -2 ms pulses
    # speed in %
    dc = (speed / 100.0) * (1/20) + (1/20)
    return dc

# create pwm channel on pin P12
pwm = PWM(0, frequency=50)  # use PWM timer 0, with a frequency of 50Hz
pwm_c = pwm.channel(0, pin='P12', duty_cycle=speed_to_dc(0))


# initialize `P9` in gpio mode and make it an output
p_out = Pin('P9', mode=Pin.OUT)
p_out.value(1)
p_out.value(0)
p_out.toggle()
p_out(True)

# make `P10` an input with the pull-up enabled
p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
p_in() # get value, 0 or 1

time.sleep(2)

i = 0
while p_in() == 1:
    pwm_c.duty_cycle(speed_to_dc(i*10)) # change the duty cycle to 20%
    if i < 10:
        i = i++1
    pycom.rgbled(0x008000)  # Green
    time.sleep(1)
    pycom.rgbled(0x000080)  # Blue
    time.sleep(1)
    p_out.toggle()

pwm_c.duty_cycle(speed_to_dc(0)) # change the duty cycle to 20%

pycom.rgbled(0x800000)  # Red
