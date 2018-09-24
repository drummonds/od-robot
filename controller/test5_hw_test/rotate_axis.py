from machine import Pin, PWM
import pycom
import time

class Rotate:
    # Servo to fixed position
    def __init__(self, pwm):
        # Assum 50ms timer already set up and going to reuse
        self.pwm = pwm
        self.is_active = False
        self.at_position = 50

    def run(self):
        pass

    def state_text(self):
        return 'Rotate position = {}'.format(self.at_position)

    def activate(self, start_dc=0.15):
        # May not be switched on
        if not self.is_active:
            self.is_active = True
            self.pwm_c = self.pwm.channel(2, pin='G13', duty_cycle=start_dc)

    def set_position(self, position): # Converts to 1 -2 ms pulses
        self.at_position = position
        # speed in %
        dc = (position / 100.0) * (1/20) + (1/20)
        self.activate(start_dc=dc)
        self.pwm_c.duty_cycle(dc)
        return dc

    def wait_set_position(self, position):
        """Rotates and waits until rotate gets there.  Guess time from
        assuming a constant rotation speed"""
        full_rotate_time = 3000  # ms
        #  Estiamte on rotation at full speed
        time_estimate = full_rotate_time * abs(self.at_position - position) / 100
        #  Allow for creep which can take a minimum time
        if self.at_position - position != 0:
            time_estimate = min(int(time_estimate), 1500)
        self.set_position(position)
        time.sleep_ms(int(time_estimate))

    def shutdown(self):
        # Ideally won't move servo
        self.pwm_off = Pin('G13', mode=Pin.IN, pull=Pin.PULL_UP)
        self.is_active = False

    def in_bin(self):
        self.wait_set_position(86)

    def out_bin(self):
        self.wait_set_position(12)  # min diff seems to be 2
        self.wait_set_position(14)

    def dvd(self):
        self.wait_set_position(50)
