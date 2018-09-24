from mqtt import MQTTClient
import machine
import network
import pycom
import time
from time import sleep
import ujson

print("MyMqtt Test 6 V1.14 2018-08-28")

def sub_cb(topic, msg):
   print(msg)

def socket_status(s):
    print("checking Network status")
    wlan = network.WLAN()
    print(" Connect  {}".format(wlan.isconnected()))
    print(" ifconfig {}".format(wlan.ifconfig()))
    #print("NIC")
    #print("  {}".format(s.nic))
    print("All")
    print("  {}".format(s))

class MyMqtt:
    DELAY = 2
    DEBUG = True

    def __init__(self):
        with open("secret.json", "r") as f:
            secrets = ujson.load(f)
        self.broker = "io.adafruit.com"
        # self.broker = "10.0.0.137"
        self.secrets = secrets
        self.user = self.secrets["MQTT_USER"]
        self.password = self.secrets["MQTT_PASSWORD"]
        self.group = self.secrets["MQTT_GROUP"]
        print("User: {}, Password: {}, Group: {}".format(
            self.user, self.password, self.group))

        self.client =  MQTTClient("device_id", "io.adafruit.com",user=self.user,
            password=self.password, port=1883, keepalive=1)

        self.client.set_callback(sub_cb)
        self.client.connect()  # This can fail
        #self.client.subscribe(topic="{}/feeds/{}.{}".format(
        #    self.user, self.group, "led"))


    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)


    def reconnect(self):
        try:
            self.client.disconnect()  # This can fail
        except OSError as e:
            self.log(True,  "MQ.disconnect {}".format(e))
        try:
            self.client = MQTTClient("device_id", "io.adafruit.com",user=self.user,
                password=self.password, port=1883, keepalive=1)
        except OSError as e:
            self.log(True,  "MQ.__INIT {}".format(e))
        try:
            self.client.connect()  # This can fail
        except OSError as e:
            self.log(True,  "MQ.connect {}".format(e))


    def send_value(self, value, feed):
        topic = "{}/feeds/{}.{}".format(self.user, self.group, feed)
        print(" SV topic = |{}|".format(topic))
        msg = '{}'.format(value)
        print(" SV msg   = |{}|".format(msg))
        s = self.client.publish(
            topic=topic, msg=msg)
        return s


    def poll(self):
        self.client.check_msg()
