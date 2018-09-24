# Adding MQTT
import pycom
import time

print("test1 version 0.2 2018-08-21impo")
pycom.heartbeat(False)

for i in range(2):
    pycom.rgbled(0xFF0000)  # Red
    time.sleep(1)
    pycom.rgbled(0x00FF00)  # Green
    time.sleep(1)
    pycom.rgbled(0x0000FF)  # Blue
    time.sleep(1)
pycom.rgbled(0x402000)  # Orange
