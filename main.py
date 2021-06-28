import configparser
import json

import paho.mqtt.client as mqtt
from flask import Flask, request

from dataforwarding import parser

# Check "settings.conf.example"
CONF_FILE = "settings.conf"
AISTIN = "aistin"
_NB_100 = "nb_100"

app = Flask(__name__)

config = configparser.ConfigParser()
config.read(CONF_FILE)

mqtt_user = config.get("MqttBroker", "user")
mqtt_passwd = config.get("MqttBroker", "passwd")
mqtt_host = config.get("MqttBroker", "host")
mqtt_port = config.getint("MqttBroker", "port")


client = mqtt.Client(config.get("MqttBroker", "Host"))

@app.route("/input/<source>", methods=["GET", "POST"])  # @ means decorator
@app.route("/input", methods=["GET", "POST"])
def read_json_object(source=None):
    sensor = parser.Sensor.nb_100
    if source == AISTIN:
        sensor = parser.Sensor.aistin
    data = request.get_json()
    parsed = parser.parse(data, sensor)
    send_to_mqtt(parsed, sensor)
    return "Data accepted by oulu-smartcampus-dataforwarding"

def send_to_mqtt(message, sensor):
    topic = "nb100_out_topic"
    if sensor == parser.Sensor.aistin:
        topic = "aistin_out_topic"
    client.publish(config.get("MqttBroker", topic), json.dumps(message))

client.username_pw_set(mqtt_user, mqtt_passwd)
client.connect(mqtt_host, mqtt_port)
client.loop_start()

app.run(host='0.0.0.0', port=config.get("Http", "port"), use_reloader=False, debug=False)
