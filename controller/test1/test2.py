from network import WLAN
wlan = WLAN(mode=WLAN.STA)
import pycom
import time

# initialisation code
pycom.heartbeat(False)
pycom.rgbled(0x008080)  # Cyan

# Connect to Wifi
nets = wlan.scan()
for net in nets:
    if net.ssid == 'HDTL-a':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'FEEDDA1961'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break
while True:
    pycom.rgbled(0x800000)  # Red
    time.sleep(1)
    pycom.rgbled(0x008000)  # Green
    time.sleep(1)
    pycom.rgbled(0x000080)  # Blue
    time.sleep(1)
