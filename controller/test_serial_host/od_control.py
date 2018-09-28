import time
import serial


class ODRobotError(Exception):
    pass


class Rotator:
    def __init__(self, robot):
        self.old_pos = -1
        self.robot = robot
        self.in_home = 86
        self.dvd_home = 50.5
        self.out_home = 14
        self.waste_home = 0

    def rotate(self, new_position, verbose = False):
        self.rotate_head_anti_hystersis(new_position, verbose = verbose)

    def rotate_head_anti_hystersis(self, new_position, verbose = False):
        if new_position != self.old_pos:
            pre_move = max(0, new_position - 5)
            self.robot(f'control1.rotate.wait_set_position({pre_move})', verbose = False)
            time.sleep(1)  # Needs to wait a little longer to settle
            self.robot(
                f'control1.rotate.wait_set_position({new_position})', verbose = verbose)
            self.old_pos = new_position  # Store the old position

    def in_bin(self, offset = 0, verbose = False):
        self.rotate_head_anti_hystersis(self.in_home + offset, verbose = verbose)

    def dvd(self, offset = 0, verbose = False):
        self.rotate_head_anti_hystersis(self.dvd_home + offset, verbose = verbose)

    def out_bin(self, offset = 0, verbose = False):
        self.rotate_head_anti_hystersis(self.out_home + offset, verbose = verbose)

    def waste_bin(self, offset = 0, verbose = False):
        self.rotate_head_anti_hystersis(self.waste_home + offset, verbose = verbose)



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

    def pickup_from_dvd_drive(self):
        self.disk_open()
        self.rotator.dvd(offset = 0.5)
        self.release()
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=120)')  # Move to surface
        if not self.z_at_bottom():
            self.make_safe()
            raise ODRobotError('Failed to grip Optical Disc on pickup from DVD')
        self.grip()
        time.sleep(1)  # Let it be securely gripped?
        self.raise_toolhead()

    def drop_on_dvd_drive(self):
        self.disk_open()
        self.rotator.dvd(offset = -0.2)
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=40)')  # Move nearer dvd
        self.release()
        time.sleep(1)  # Let release take effect
        self.make_safe()

    def pickup_from_in_bin(self):
        self.rotator.in_bin()
        self.release()
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=150)')  # Deeper than DVD so move further
        self.grip()
        self.raise_toolhead()

    def drop_on_in_bin(self):
        self.rotator.in_bin()
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=10)')  # Move nearer dvd
        self.release()
        time.sleep(1)  # Let release take effect
        self.make_safe()

    def pickup_from_out_bin(self):
        self.rotator.out_bin()
        self.release()
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=150)')  # Deeper than DVD so move further
        self.grip()
        self.raise_toolhead()

    def drop_on_out_bin(self):
        self.rotator.out_bin()
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=20)')  # Move nearer bin
        time.sleep(2)  # TODO poll
        self.release()
        self.park()
        self.shutdown()

    def drop_on_bin(self, destination_bin):
        destination_bin()
        self.robot(f'control1.z_axis.nudge({self.z_axis_down_setting}, run_time=20)')  # Move nearer bin
        time.sleep(2)  # TODO poll
        self.release()
        self.park()
        self.shutdown()

    def rotate(self, new_position):
        self.rotator.rotate(new_position)

    def load(self, verbose=False):
        self.make_safe(verbose=verbose)
        self.pickup_from_in_bin()
        self.drop_on_dvd_drive()
        self.make_safe(verbose=verbose)
        self.disk_close()

    def unload(self, verbose=False, destination_bin = None):
        if destination_bin is None:
            destination_bin = self.rotator.out_bin
        self.make_safe(verbose=verbose)
        self.pickup_from_dvd_drive()
        time.sleep(1)  # Otherwise seems to close very close to disk
        self.disk_close()
        self.drop_on_out_bin()
        self.drop_on_bin(destination_bin)
        self.make_safe(verbose=verbose)
        self.disk_close()


