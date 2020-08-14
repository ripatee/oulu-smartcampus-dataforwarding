import configparser
import datetime
import json
import time

import paho.mqtt.client as mqtt
from flask import Flask, request

# Check "settings.conf.example"
CONF_FILE = "settings.conf"

app = Flask(__name__)

config = configparser.ConfigParser()
config.read(CONF_FILE)

mqtt_user = config.get("MqttBroker", "user")
mqtt_passwd = config.get("MqttBroker", "passwd")
mqtt_host = config.get("MqttBroker", "host")
mqtt_port = config.getint("MqttBroker", "port")

client = mqtt.Client(config.get("MqttBroker", "Host"))

@app.route("/input", methods=["GET", "POST"])  # @ means decorator
def read_json_object():
    data = request.get_json()
    parsed = parse(data)
    send_to_mqtt(parsed)
    return "Data accepted by oulu-smartcampus-dataforwarding"

def send_to_mqtt(message):
    client.publish(config.get("MqttBroker", "out_topic"), json.dumps(message))
 
def parse(package):  # Received data from sensor
    try:
        output = {}
        # Pick index of value and place it in output
        output["deveui"] = package["deviceName"]
        output["timestamp_parser"] = time.time()
        try:
            # timestamp_node is time as indicated by upstream, output uses epoch seconds
            time_sent = datetime.datetime.strptime(package["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
            output["timestamp_node"] = int(time_sent.replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            print("unexpected node timestamp")
        output["temperature"] = round(float(package["data"][0]["value"][1]), 1)
        output["humidity"] = round(float(package["data"][0]["value"][0]))
        output["pressure"] = round(float(package["data"][1]["value"][0]))
        output["rssi"] = int(float(package["data"][2]["value"][0]))
        output["battery"] = int(package["data"][3]["value"][0])/1000 # Value/unit error from sensor
        output["timestamp_parser"] = int(time.time())
        return output
    except (TypeError, IndexError, KeyError):
        print("unexpected packet")

client.username_pw_set(mqtt_user, mqtt_passwd)
client.connect(mqtt_host, mqtt_port)
client.loop_start()
