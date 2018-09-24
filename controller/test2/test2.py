import pycom
import time
import ujson

pycom.heartbeat(False)

pycom.rgbled(0x800080)  # Purple
time.sleep(1)
a = ujson.load(open("secret.json", "r"))
print(a)
pycom.rgbled(0x00FF00)  # Green
time.sleep(1)
for k, v in a.items():
    print("{}={}".format(k, v))

pycom.rgbled(0x0000FF)  # Blue
time.sleep(1)
pycom.rgbled(0x302000)  # Orange
