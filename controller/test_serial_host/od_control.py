import time
import serial


class ODRobotError(Exception):
    pass


class Rotator:
    def __init__(self, robot):
        self.old_pos = -1
        self.robot = robot
        # When rotating to a bin sometimes use an offset for pickup and drop off
        # Some bins may need longer to pickup from
        self.bins = {
            # Name: position, drop offset, pickup offset, drop descend_time, pickup descent time
            #       0         1            2              3                  4
            'in': [ 86,       0,           0,             20,                150],
            'out': [14,       0,           0,             20,                150],
            'od': [50.5,      0,           0,             40,                55],
            'waste': [0,      0,           0,             20,                0],  # no pickup
        }

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
        self.rotator = Rotator(self.robot)
        self.toolhead_z = -999  # Unknown state.  This is a best guess of its position
        # 0 is at top and then ca 1 = 0.1 seconds down
        # Constants
        self.z_axis_down_setting = 50
        self.z_axis_up_setting = 44

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

    def zero_toolhead(self, verbose = False):
        self.move_toolhead(-200, verbose=verbose)  # Rely on code to stop it
        self.toolhead_z = 0

    def move_toolhead_to(self, position, verbose = False):
        # Going to move in 1 second bursts and then measure position
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
        # Going to move in 1 second bursts and then measure position
        if amount > 0:  # move down
            self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time={amount})',
                       verbose=verbose)
        else:  # move up
            self.robot(f'control1.z_axis.nudge({self.z_axis_up_setting}, run_time={-amount})',
                       verbose=verbose)
        self.toolhead_z += amount

    def toolhead_safe(self, verbose=False):
        """Put to park and shutdown"""
        self.robot('control1.th.park()', verbose=verbose)  # Make toolhead safe
        time.sleep(2)  # TODO Poll status
        self.robot('control1.th.shutdown()', verbose=verbose)  # Make toolhead safe

    def raise_toolhead(self, verbose=False):
        """Raise the toolhead and wait for it to be finished"""
        self.zero_toolhead(verbose=verbose)
        self.robot('control1.z_axis.shutdown()', verbose=verbose)

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

    def drop_on_bin(self, destination_bin, verbose=False):
        self.rotator.to_bin(destination_bin, verbose=verbose, drop_off=True)
        time_out = self.rotator.drop_descend_time(destination_bin)
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting},' +
                   f'run_time={time_out})')  # Move nearer bin
        time.sleep(2)  # TODO poll
        self.release()
        self.park()
        self.shutdown()

    def pickup_from_bin(self, destination_bin, verbose=False):
        """Note this leaves the toolhead in the grip position which is not stable for a long time"""
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


