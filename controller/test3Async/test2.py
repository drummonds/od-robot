# TEsting running from REPL
import pycom
import ujson
import time

def main():
    print("test2 version 0.3 2018-08-21")

    with open("secret.json", "r") as f:
        secrets = ujson.load(f)
    print(secrets)
    pycom.heartbeat(False)

    for i in range(2):
        pycom.rgbled(0xFF0000)  # Red
        time.sleep(1)
        pycom.rgbled(0x00FF00)  # Green
        time.sleep(1)
        pycom.rgbled(0x0000FF)  # Blue
        time.sleep(1)
    pycom.rgbled(0x402000)  # Orange

main()
