import configparser
import json

import paho.mqtt.client as mqtt
from flask import Flask, request

from dataforwarding import nb100

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
    parsed = nb100.parse(data)
    send_to_mqtt(parsed)
    return "Data accepted by oulu-smartcampus-dataforwarding"

def send_to_mqtt(message):
    client.publish(config.get("MqttBroker", "out_topic"), json.dumps(message))

client.username_pw_set(mqtt_user, mqtt_passwd)
client.connect(mqtt_host, mqtt_port)
client.loop_start()

app.run(host='0.0.0.0', port=config.get("Http", "port"), use_reloader=False, debug=False)
