from flask import Flask, request
import paho.mqtt.client as mqtt
import time
import datetime
import json

MQTT_ADDR = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASSWD = ""
MQTT_CLIENTNAME = "NB100-testclient"
MQTT_TOPIC = "Sensor-test"

app = Flask(__name__)
data = None

client = mqtt.Client(MQTT_CLIENTNAME)

@app.route('/5gtn/input', methods=['GET', 'POST'])
def readJsonObject():           #Reads POST request, sends it to parser
    data = request.get_json()   #and sends parsed message to MQTT-broker
    parsed = dataParser(data)
    sendToMqtt(parsed)
    return "Data accepted"

def sendToMqtt(message):
    client.connect(MQTT_ADDR, MQTT_PORT)
    client.loop_start()
    client.publish(MQTT_TOPIC, json.dumps(message))
    client.loop_stop()
    client.disconnect

def dataParser(package):				#received data from sensor
	try:
		output = {}
		#pick index of value and place it in output
		output['_msgid'] =  time.ctime().replace(" ", "-")
		output['deveui'] = package['deviceName']
		time_sent = datetime.datetime.strptime(package["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
		output['timestamp_node'] = int(time_sent.replace(tzinfo=datetime.timezone.utc).timestamp())
		output['temperature'] = round(float(package['data'][0]['value'][1]))
		output['humidity'] = round(float(package['data'][0]['value'][0]))
		output['pressure'] = round(float(package['data'][1]['value'][0]))
		output['rssi'] = int(float(package['data'][2]['value'][0]))
		output['light'] = 0
		output ['pir'] = 0
		output ['co2'] = 0
		output ['battery'] = int(package["data"][3]['value'][0])/1000 #value/unit error from sensor
		output['timestamp_parser'] = int(time.time())
		output['sound_avg'] = 0
		output['sound_peak'] = 0
		return output
	except (TypeError, IndexError, KeyError):
		print("unexpected packet")