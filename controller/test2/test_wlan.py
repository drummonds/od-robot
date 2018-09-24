import machine
from network import WLAN
import pycom
from time import sleep

import ujson
secrets = ujson.load(open("secret.json", "r"))

def hello():
    print("Hello to WLAN test 0.1")
    wlan = WLAN(mode=WLAN.STA)
    lans = wlan.scan()
    print("Wlan scan found {} networks.".format(len(lans)))
    for lan in lans:
        print('  Lan = {}'.format(lan))

    print("Connecting to Wifi\n")
    pycom.rgbled(0x001010)
    sleep(0.5)
    wlan.connect(secrets["SSID"], auth=(WLAN.WPA2, secrets["WIFIPassword"]), timeout=5000)
    count = 100
    while not wlan.isconnected():
        sleep(0.1)
        machine.idle()
        count -= 1
        if count < 0:
            pycom.rgbled(0x300030)
            raise WLANError('10 second time out on connecting to WIFI')
    pycom.rgbled(0x007030)
    print("Connected to Wifi\n")

hello()
