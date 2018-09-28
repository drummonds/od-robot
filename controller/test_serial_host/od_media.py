"""
This is a python file to control and get information about optical drives.

Eventually aim to handle CD, DVD , BluRay on Windows and Linux
"""

import string
from ctypes import windll


class ODMediaError(Exception):
    pass

def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    print(bitmask)
    for letter in 'ABCDEFGHIJKLMNOPQ':
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives

def drive_is_d():
    drive_list = get_drives()
    assert len(drive_list) == 2
    assert drive_list[1] == 'D'
    return True

def open_dvd():
    windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)

def close_dvd():
    windll.WINMM.mciSendStringW(u"set cdaudio door closed", None, 0, None)

