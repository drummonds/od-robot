from mqtt_as import config, ESP32

# Include any cross-project settings.

if ESP32:
    config['ssid'] = 'HDTL-a'  # EDIT if you're using ESP32
    config['wifi_pw'] = 'FEEDDA1961'
