# This version is essentially a bodge by reopening the socket
# before sending a value.  However useless for receiving data.
from mqtt import MQTTClient
import machine
import pycom
import time
from time import sleep
import ujson

# print("MyMqtt V0.3 2018-08-23")

def sub_cb(topic, msg):
   print(msg)

class MyMqtt:
    def __init__(self):
        with open("secret.json", "r") as f:
            secrets = ujson.load(f)
        self.secrets = secrets
        self.user = self.secrets["MQTT_USER"]
        self.password = secrets["MQTT_PASSWORD"]
        self.group = self.secrets["MQTT_GROUP"]

        self.client = MQTTClient("device_id", "io.adafruit.com",user=self.user,
            password=self.password, port=1883, keepalive=1)
        self.listen_client = MQTTClient("device_id", "io.adafruit.com",user=self.user,
            password=self.password, port=1883, keepalive=1)

        self.listen_client.set_callback(sub_cb)
        self.listen_client.connect()
        self.listen_client.subscribe(topic="{}/feeds/{}.{}".format(
            self.user, self.group, "led"))

    def send_value(self, value, feed="button"):
        # print('Sending {} to Adafruit or pretending to'.format(value))
        # Trying to connect and then disconnect as running with uasyncio
        # it didn't seem to work repeatedly and this does.
        self.client.connect()
        self.client.publish(
            topic="{}/feeds/{}.{}".format(self.user, self.group, feed),
            msg='{}'.format(value))
        self.client.disconnect()
        return value

    def poll(self):
        #self.client.set_callback(sub_cb)
        #self.client.connect()
        #self.client.subscribe(topic="{}/feeds/{}.{}".format(
        #        self.user, self.group, "led"))
        self.listen_client.check_msg()
        #self.client.disconnect()
