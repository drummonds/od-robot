from machine import Pin, PWM
import pycom
import time

class ZAxis:
    def __init__(self, pwm):
        # Assum 50ms timer already set up and going to reuse
        self.pwm = pwm
        self.switch_top = Pin('G0', mode=Pin.IN, pull=Pin.PULL_UP)
        self.switch_bottom = Pin('G3', mode=Pin.IN, pull=Pin.PULL_UP)
        self.is_active = False
        self.neutral = 47  # Calibration constant, PWM position that does
        # not move head (Zero speed)

    def run(self):
        pass

    @property
    def bottom(self):
        return not self.switch_bottom()

    @property
    def top(self):
        return not self.switch_top()

    def state(self):
        if not self.bottom and not self.top:
            return 0
        elif self.bottom and (not self.top):
            return 1
        elif not self.bottom and self.top:
            return 2
        else:
            return 3

    def state_text(self):
        state = self.state()
        if state == 0:
            return 'Middle'
        elif state == 1:
            return 'Bottom'
        elif state == 2:
            return 'Top'
        else:
            return 'OD at top or Error'.format(self.top, self.bottom)

    def activate(self, start_dc=0.15):
        # May not be switched on
        if not self.is_active:
            self.is_active = True
            self.pwm_c = self.pwm.channel(1, pin='G14', duty_cycle=start_dc)

    def set_position(self, position): # Converts to 1 -2 ms pulses
        # speed in %
        dc = (position / 100.0) * (1/20) + (1/20)
        self.activate(start_dc=dc)
        self.pwm_c.duty_cycle(dc)
        return dc

    def shutdown(self):
        # Ideally won't move servo
        self.pwm_off = Pin('G14', mode=Pin.IN, pull=Pin.PULL_UP)
        self.is_active = False

    def nudge(self, at_position, run_time=20, override=False):
        """run_time set in 100ms units"""
        time_out = run_time * 100  # This is the maximum time
        # Nudge the servo for testing.  Run for 1 second at at_position
        for i in range(time_out):
            if not override:  # Check end stops
                if at_position > self.neutral:  # moving down
                    if self.bottom:
                        break
                else:  # moving up
                    if self.top:
                        break
            if i == 0:
                self.set_position(at_position)  # Only start moving if ok
            time.sleep_ms(1)
        self.shutdown()
        print("Shutdown Z Axis nudge")
