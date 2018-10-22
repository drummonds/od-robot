"""
This is a python file to control and get information about optical drives.

Eventually aim to handle CD, DVD , BluRay on Windows and Linux
"""

import subprocess


class ODMedia:
    def __init__(self):
        self.path_root = r"C:\Program Files (x86)\CDBurnerXP\cdbxpcmd.exe"
        # Safety check for known situation
        if self.number_of_drives == 1:
            print('Found D drive all ok')
        else:
            raise Exception(f"Didn't find 1 drive, num = {media.number_of_drives}")

    def version(self):
        result = subprocess.run([self.path_root, "--version"], stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')

    def list_drives(self):
        def parse_media(line):
            a = line.split(':', maxsplit=1)
            drive_number = int(a[0])
            b = a[1].strip().split(' (', maxsplit=1)
            drive_name = b[0].strip()
            drive_letter = b[1][0]
            return [drive_number, drive_name, drive_letter]

        result = subprocess.run([self.path_root, "--list_drives"], stdout=subprocess.PIPE
                                )
        lines = result.stdout.decode('utf-8').strip().split('\n')  # split into lines
        trim_lines = [x.strip() for x in lines]
        return [parse_media(x) for x in trim_lines]

    @property
    def number_of_drives(self):
        return len(self.list_drives())

    def disk_open(self):
        result = subprocess.run([self.path_root, "--eject", "--drivename:0"], stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')

    def disk_close(self):
        result = subprocess.run([self.path_root, "--load", "--drivename:0"], stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')

    def burn_disk(self, file_name):
        """ eg """
        result = subprocess.run([self.path_root, "--burn-iso", "-device:0",
                                 f'-file:{file_name}'], stdout=subprocess.PIPE)
        print(result)
        return result.stdout.decode('utf-8')
