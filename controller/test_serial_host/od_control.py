import time
import serial

class ODRobotError(Exception):
    pass

class Rotator:
    def __init__(self, robot):
        self.old_pos = -1
        self.robot = robot

    def close(self):
        self.ser.close()

    def rotate_head_anti_hystersis(self, new_position):
        if new_position != self.old_pos:
            pre_move = max(0, new_position - 5)
            self.robot(f'control1.rotate.wait_set_position({pre_move})')
            time.sleep(1)  # Needs to wait a little longer to settle
            self.robot(
                f'control1.rotate.wait_set_position({new_position})')
            self.old_pos = new_position  # Store the old poistion

    def in_bin(self):
        self.rotate_head_anti_hystersis(86)

    def dvd(self):
        self.rotate_head_anti_hystersis(49)

    def out_bin(self):
        self.rotate_head_anti_hystersis(14)

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
        self.rotate = Rotator(self.robot)

    def robot(self, command):
        self.ser.write((command + '\r\n').encode('utf-8'))
        out = ''
        # let's wait two seconds before reading output (let's give device time to answer)
        time.sleep(2)  # TODO make waiting more intelligent, ie wait only if have to.
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1).decode('utf-8')
        if out != '':
            print("Robot>" + out)

    def toolhead_safe(self):
        """Put to park and shutdown"""
        self.robot('control1.th.park()')  # Make toolhead safe
        time.sleep(2)  # TODO Poll status
        self.robot('control1.th.shutdown()')  # Make toolhead safe


    def raise_toolhead(self):
        """Raise the toolhead and wait for it to be finished"""
        self.robot('control1.z_axis.nudge(44, run_time=90)')  # Move to top
        time.sleep(2)  # TODO Poll status
        self.robot('control1.z_axis.shutdown()')


    def make_safe(self):
        """Put the robot into a safe position to start or end a series of moves"""
        self.toolhead_safe()
        self.raise_toolhead()

    def pickup_from_dvd_drive(self):
        self.disk_open()
        self.rotate.dvd()
        self.robot('control1.th.release()')
        self.robot('control1.z_axis.nudge(49, run_time=90)')  # Move to surface
        self.robot('control1.th.grip()')
        time.sleep(1)  # Let it be securely gripped?
        self.raise_toolhead()


    def pickup_from_in_bin(self):
        self.rotate.in_bin()
        self.robot('control1.th.release()')
        self.robot('control1.z_axis.nudge(49, run_time=120)')  # Deeper than DVD so move further
        self.robot('control1.th.grip()')
        time.sleep(1)  # Let it be securely gripped?
        self.raise_toolhead()


    def drop_on_dvd_drive(self):
        self.disk_open()
        self.rotate.dvd()
        self.robot('control1.z_axis.nudge(49, run_time=40)')  # Move nearer dvd
        time.sleep(4)  # TODO poll
        self.robot('control1.th.release()')
        time.sleep(1)  # Let the release happen
        self.robot('control1.th.park()')
        time.sleep(2)  # Let the park happen before shutdown
        self.robot('control1.th.shutdown()')


    def drop_on_out_bin(self):
        self.rotate.out_bin()
        self.robot('control1.z_axis.nudge(49, run_time=20)')  # Move nearer bin
        time.sleep(2)  # TODO poll
        self.robot('control1.th.release()')
        time.sleep(1)  # Let the release happen
        self.robot('control1.th.park()')
        time.sleep(2)  # Let the park happen before shutdown
        self.robot('control1.th.shutdown()')

    def load(self):
        self.make_safe()
        self.pickup_from_in_bin()
        self.drop_on_dvd_drive()
        self.make_safe()
        self.disk_close()

    def unload(self):
        self.make_safe()
        self.pickup_from_dvd_drive()
        time.sleep(1)  # Otherwise seems to close very close to disk
        self.disk_close()
        self.drop_on_out_bin()
        self.make_safe()
        self.disk_close()


