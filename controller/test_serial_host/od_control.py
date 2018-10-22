import json
import time
import serial

from h3timeit import h3_timeit

class ODRobotError(Exception):
    pass


class Rotator:
    def __init__(self, robot, calibration):
        self.old_pos = -1
        self.robot = robot
        # When rotating to a bin sometimes use an offset for pickup and drop off
        # Some bins may need longer to pickup from
        self.bins = calibration['bins']

    def rotate(self, new_position, verbose = False):
        self.rotate_head_anti_hysteresis(new_position, verbose = verbose)

    def rotate_head_anti_hysteresis(self, new_position, verbose = False):
        if new_position != self.old_pos:
            pre_move = max(0, new_position - 5)
            self.robot(f'control1.rotate.wait_set_position({pre_move})', verbose = False)
            time.sleep(1)  # Needs to wait a little longer to settle
            self.robot(
                f'control1.rotate.wait_set_position({new_position})', verbose = verbose)
            self.old_pos = new_position  # Store the old position

    def drop_descend_time(self, bin_name):
        this_bin = self.bins[bin_name]
        return this_bin[3]

    def pickup_descend_time(self, bin_name):
        """This is more a safety maximum as the switch should trigger"""
        this_bin = self.bins[bin_name]
        return this_bin[4]

    def to_bin(self, bin_name, verbose=False, drop_off=False):
        this_bin = self.bins[bin_name]
        if drop_off:
            offset = this_bin[1]
        else:
            offset = this_bin[2]
        self.rotate_head_anti_hysteresis(this_bin[0] + offset, verbose=verbose)


class ODRobot:
    def __init__(self, disk_open, disk_close, com_port="COM6"):
        # Constants
        try:
            self.load_calibration()
        except FileNotFoundError:
            self.default_calibration()
            self.save_calibration()
        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.com_port = com_port
        self.disk_open = disk_open
        self.disk_close = disk_close
        self.ser = serial.Serial(
            port=com_port,
            baudrate=115200
        )
        if not self.ser.isOpen():
            raise ODRobotError(f"Problem opening serial port on {com_port}")
        self.robot('import control1')  # Tends to do a soft reset at end of prog
        self.rotator = Rotator(self.robot, self.calibration)
        self.toolhead_z = -999  # Unknown state.  This is a best guess of its position
        # 0 is at top and then ca 1 = 0.1 seconds down

    # ****Calibration settings****

    @property
    def z_axis_down_setting(self):
        return self.calibration['z_axis_down_setting']

    @property
    def z_axis_up_setting(self):
        return self.calibration['z_axis_up_setting']

    @property
    def z_axis_middle_setting(self):
        return (self.z_axis_down_setting + self.z_axis_up_setting) / 2

    def default_calibration(self):
        self.calibration = {}
        self.calibration['z_axis_down_setting'] = 51
        self.calibration['z_axis_up_setting'] = 44
        self.calibration['bins'] = {
            # Name: position, drop offset, pickup offset, drop descend_time, pickup descent time
            #       0         1            2              3                  4
            'in': [86, 0, 0, 10, 150],
            'out': [14, 0, 0, 10, 150],
            'od': [51.0, -0.2, 0.5, 40, 70],
            'waste': [0, 0, 0, 10, 0],  # no pickup
        }
        self.calibration['toolhead_speed_up'] = 10  # mm/sec initial guess
        self.calibration['toolhead_speed_down'] = 10  # mm/sec initial guess

    def load_calibration(self):
        with open('od_robot_calibration.json', 'r') as data_file:
            json_data = data_file.read()
        self.calibration = json.loads(json_data)

    def save_calibration(self):
        with open('od_robot_calibration.json', 'w') as outfile:
            json.dump(self.calibration, outfile)

    # ****Tool head timing and calibration settings****
    @h3_timeit
    def move_down(self, speed_setting=60, time_setting=3):
        """Move down from top for a time period and measure time to complete (either timeout or
         hit stop)"""
        if not self.z_at_top():
            raise ODRobotError('When started move_down toolhead not at top')
        self.robot(f'control1.z_axis.nudge({speed_setting}, run_time={time_setting})', verbose=True)

    # Move up definitely
    @h3_timeit
    def move_up(self, speed_setting=40, time_setting=12):
        """ move back to the top for a time period"""
        self.robot(f'control1.z_axis.nudge({speed_setting}, run_time={time_setting})', verbose=True)
        if not self.z_at_top():
            raise ODRobotError('When move_up toolhead not finis top')

    def measure_up_down(self, speed_offset=None, offset_middle=None, time_down=10, time_up=None):
        """offset is the amount from the centre that is used as the speed"""
        if offset_middle is None:
            offset_middle = self.z_axis_middle_setting
        if speed_offset is None:
            speed_offset = 5  # Changin default to 5 to give a wider range for center drift
        if time_up is None:
            time_up = time_down * 3
        down_speed = offset_middle + speed_offset
        up_speed = offset_middle - speed_offset
        md = self.move_down(speed_setting=down_speed, time_setting=time_down)
        mu = self.move_up(speed_setting=up_speed, time_setting=time_up)
        # Assume a symmetrical V shaped transfer curve then the center (no movement)
        # Calculate better estimate of middle
        alpha = mu[0] / md[0]  # Parameter for ratio of times
        new_offset_middle = (down_speed + alpha * up_speed) / (1 + alpha)
        return ((down_speed, md[0],), (up_speed, mu[0],), new_offset_middle,)

    def move_toolhead_to(self, position, verbose = False):
        """Move to:
        position in mm"""
        if self.toolhead_z < 1:
            self.zero_toolhead(verbose)
        if position < 1:
            self.zero_toolhead(verbose)
        elif position == self.toolhead_z:
            pass  # No move necessary
        else:
            new_position = position - self.toolhead_z
            self.move_toolhead(new_position, verbose)

    def move_toolhead(self, amount, verbose = False):
        """Move to:
        position in mm"""
        if amount > 0:  # move down
            calc_run_time = amount * 10 / self.calibration['toolhead_speed_up']
            self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time={calc_run_time})',
                       verbose=verbose)
        else:  # move up
            calc_run_time = amount * 10 / self.calibration['toolhead_speed_down']
            self.robot(f'control1.z_axis.nudge({self.z_axis_up_setting}, run_time={-calc_run_time})',
                       verbose=verbose)
        self.toolhead_z += amount

    def zero_toolhead(self, verbose = False):
        self.move_toolhead(-200, verbose=verbose)  # Rely on code to stop it
        self.toolhead_z = 0

    def toolhead_safe(self, verbose=False):
        """Put to park and shutdown"""
        self.robot('control1.th.park()', verbose=verbose)  # Make toolhead safe
        time.sleep(2)  # TODO Poll status
        self.robot('control1.th.shutdown()', verbose=verbose)  # Make toolhead safe

    def raise_toolhead(self, verbose=False):
        """Raise the toolhead and wait for it to be finished"""
        self.zero_toolhead(verbose=verbose)
        self.robot('control1.z_axis.shutdown()', verbose=verbose)

    # ******************************************************************
    # ****Other code****
    def close(self):
        self.ser.close()

    def state(self):
        value = self.robot('control1.z_axis.state()', verbose=False)
        try:
            result = int(value[1])
            return result
        except:
            raise ODRobotError(f'Result was |{value}|, trying to get second part as number')

    def z_at_top(self):
        return self.state() == 2

    def z_at_bottom(self):
        return self.state() == 1

    def z_in_middle(self):
        return self.state() == 0

    def robot(self, command, verbose = True, timeout = 20):
        """Send a command to the robot and busy wait until the command is completed.
        timeout is the maximum time, in seconds, that the command will wait before failing.
        The commmand always be repeated back and there may be optional extra information.  The final part will be
        the commmand line prompt for the next commmand '>>>'
        This is actually how the REPL command works."""
        self.ser.write((command + '\r\n').encode('utf-8'))
        out = ''
        # let's wait up to twenty seconds before reading output (let's give device time to answer)
        # wait only if have to.
        waiting = timeout * 10
        while True:
            if self.ser.inWaiting() > 0:  # Then we have characters to process
                waiting = timeout * 10 # reset timeout
                while self.ser.inWaiting() > 0:
                    out += self.ser.read(1).decode('utf-8')
                if out.find('>>>') != -1:
                    break  # The terminal string has been found
            else:  # Busy waiting
                waiting -= 1
                if waiting <=0:
                    raise ODRobotError(f'robot timeout after {timeout} seconds '
                                       + f'for command |{command}| response is |{out}|')
                time.sleep(0.1)
        if out != '':
            if verbose:
                print("Robot>" + out)
        return out.split('\n')

    def z_axis_state(self, verbose=False):
        result = self.robot('control1.z_axis.state()', verbose=verbose)[1]  # Find state
        return int(result)

    def make_safe(self, verbose=False):
        """Put the robot into a safe position to start or end a series of moves"""
        self.toolhead_safe(verbose=verbose)
        self.raise_toolhead(verbose=verbose)

    def grip(self):
        self.robot('control1.th.grip()')
        time.sleep(1)  # Let it be securely gripped?

    def release(self):
        self.robot('control1.th.release()')
        time.sleep(1)  # Let the release happen

    def park(self):
        self.robot('control1.th.park()')

    def shutdown(self):
        time.sleep(2)  # Let the eg park happen before shutdown
        self.robot('control1.th.shutdown()')

    def open_od_test(self, at_bin):
        if at_bin == 'od':
            self.disk_open()

    def drop_on_bin(self, destination_bin, verbose=False):
        self.open_od_test(destination_bin)
        self.rotator.to_bin(destination_bin, verbose=verbose, drop_off=True)
        time_out = self.rotator.drop_descend_time(destination_bin)
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting},' +
                   f'run_time={time_out})')  # Move nearer bin
        time.sleep(2)  # TODO poll
        self.release()
        self.make_safe()

    def pickup_from_bin(self, destination_bin, verbose=False):
        """Note this leaves the toolhead in the grip position which is not stable for a long time"""
        self.open_od_test(destination_bin)
        self.rotator.to_bin(destination_bin, verbose=verbose)
        self.release()
        time_out = self.rotator.pickup_descend_time(destination_bin)
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting},' +
                   f'run_time={time_out})')  # Move nearer bin
        self.grip()
        self.raise_toolhead()


    def rotate(self, new_position):
        self.rotator.rotate(new_position)

    def load(self, verbose=False, source_bin = 'in', destination_bin = 'od'):
        self.make_safe(verbose=verbose)
        self.pickup_from_bin(source_bin, verbose=verbose)
        self.drop_on_bin(destination_bin, verbose=verbose)
        self.make_safe(verbose=verbose)
        self.disk_close()

    def unload(self, verbose=False, source_bin = 'od', destination_bin = 'out'):
        self.make_safe(verbose=verbose)
        self.pickup_from_bin(source_bin, verbose=verbose)
        time.sleep(1)  # Otherwise seems to close very close to disk
        self.drop_on_bin(destination_bin, verbose=verbose)
        self.make_safe(verbose=verbose)
        self.disk_close()


