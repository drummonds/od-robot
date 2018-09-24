# This is the boot file operated once at start up
from machine import UART
import machine
from network import WLAN
import os
import ujson

# Set up USB UART
uart = UART(0, baudrate=115200)
os.dupterm(uart)

with open("secret.json", "r") as f:
    secrets = ujson.load(f)

# Set up LAN
wlan = WLAN() # get current object, without changing the mode

if machine.reset_cause() != machine.SOFT_RESET:
    wlan.init(mode=WLAN.STA)
    # configuration below MUST match your home router settings!!
    wlan.ifconfig(config=('10.0.0.50', '255.255.255.0', '10.0.0.254', '8.8.8.8'))

if not wlan.isconnected():
    # change the line below to match your network ssid, security and password
    wlan.connect(secrets["SSID"], auth=(WLAN.WPA2, secrets["WIFIPassword"]), timeout=5000)
    while not wlan.isconnected():
        machine.idle() # save power while waiting
machine.main('test7.py')
