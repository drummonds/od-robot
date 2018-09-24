from machine import Pin
import pycom
import time
from machine import PWM
pwm = PWM(0, frequency=50)  # use PWM timer 0, with a frequency of 50Hz
# create pwm channel on pin P12 with a duty cycle of 50%
pwm_c = pwm.channel(0, pin='P12', duty_cycle=0.15)

# initialisation code
pycom.heartbeat(False)
pycom.rgbled(0xCC8080)  # pale pink


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

while p_in() == 1:
    pycom.rgbled(0x008000)  # Green
    time.sleep(1)
    pycom.rgbled(0x000080)  # Blue
    time.sleep(1)
    p_out.toggle()
    pwm_c.duty_cycle(0.19) # change the duty cycle to 20%

pwm_c.duty_cycle(0.11) # change the duty cycle to 20%

pycom.rgbled(0x800000)  # Red
