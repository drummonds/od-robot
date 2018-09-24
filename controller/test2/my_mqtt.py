from mqtt import MQTTClient
import machine
import pycom
import time
from time import sleep
import ujson

def sub_cb(topic, msg):
   print(msg)

class MyMqtt:

    def __init__(self):
        secrets = ujson.load(open("secret.json", "r"))
        self.secrets = secrets
        self.user = self.secrets["MQTT_USER"]
        self.password = secrets["MQTT_PASSWORD"]
        self.group = self.secrets["MQTT_GROUP"]

        self.client = MQTTClient("device_id", "io.adafruit.com",user=self.user,
            password=self.password, port=1883)

        self.client.set_callback(sub_cb)
        self.client.connect()
        self.client.subscribe(topic="{}/feeds/{}.{}".format(
            self.user, self.group, "led"))

    def send_value(self, value, feed="button"):
        # print('Sending {} to Adafruit or pretending to'.format(value))
        self.client.publish(
            topic="{}/feeds/{}.{}".format(self.user, self.group, feed),
            msg='{}'.format(value))
        return value
