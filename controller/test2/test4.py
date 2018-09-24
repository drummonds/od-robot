from my_mqtt import MyMqtt
import pycom
VERSION = '0.0.3 2018-08-20'
# Getting read for first version

pycom.heartbeat(False)

pycom.rgbled(0xFF0000)  # Red
print("Hi {}".format(VERSION))
mq = MyMqtt()
mq.send_value("1")
pycom.rgbled(0x00FF00)  # Green
