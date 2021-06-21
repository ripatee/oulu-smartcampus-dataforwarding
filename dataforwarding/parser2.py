from time import time
import datetime
import json

class MeasurementTimestampError(Exception):
    pass

class MeasurementTypeError(Exception):
    pass


output = {}

def temperature_humidity(data):
	'''
	Temp in Celcius degrees,
	humidity in %
	'''
	temperature = round(float(data["temperature"]), 1)
	humidity = round(float(data["humidity"]), 1)
	output["temperature"], output["humidity"] = temperature, humidity


def pressure(data):
    '''
    Pressure in Bars
    '''
    output["pressure"] = float(data["pressure"]) / (1*10**3)


def acceleration(data):
    '''
    Convert each axis to G
    '''
    acceleration = {}
    acceleration["x"] = int(data["X-axis"]) / (1*10**3)
    acceleration["y"] = int(data["Y-axis"]) / (1*10**3)
    acceleration["z"] = int(data["Z-axis"]) / (1*10**3)
    output["acceleration"] = acceleration


def battery(data):
    '''
    Voltage converted to mV, percentage in %
    '''
    battery = float(data["battery voltage"]) / (1*10**3)
    battery_percentage = round(float(data["battery"]))
    output["battery"], output["battery_percentage"] = battery, battery_percentage


def orientation(data):
    '''
    Offset from horizontal level(top up) in degrees
    '''
    output["orientation"] = float(data["orientation"])


def motion(data):
    '''
    timeframes = lenght of measurement period in seconds
    motions = Amount of registered movements inside the time period
    output["motion"] = average amount of motions per 15 mins
    '''
    timeframes = data["period"] / 900
    motions = data["movement"]
    output["motion"] = int(motions / timeframes)


def moisture(data):
    '''
    Given in relative humidity RH%
    '''
    output["moisture"] = float(data["moisture"])


def co2(data):
    '''
    Given in parts per million
    '''
    output["co2"] = int(data["carbon dioxide"])


def total_movement(data):
    '''
    Total movements registered since boot
    '''
    output["total_movement"] = int(data["count"])


def differential_pressure(data):
    '''
    Difference in pressure of two areas.
    Given in Pascals for lower resolution.
    '''
    output["differential_pressure"] = float(data["pressure"])


def volatile_compounds(data):
    '''
    Given in parts per billion
    '''
    output["organic_compounds"] = int(data["Total Volatile Organic Compounds"])


def object_temperature(data):
    '''
    Object temperature in Celcius degrees
    '''
    output["object_temperature"] = float(data["temperature"])


def amplitude_frequency(data):
    '''
    amplitude in mm, frequency in Hz
    '''
    output["amplitude"] = int(data["amplitude"])
    output["frequency"] = int(data["frequency"])


def nb_100(data):
    '''
    reformat nb_100 data
    '''
    temperature_humidity(data[output["deveui"] + "-1"])
    # convert pressure to Bars
    # NOTE! received value is not in mBars as suggested.
    output["pressure"] = round(float(data[output["deveui"] + "-2"]["pressure"]) / (1*10**5), 3)
    # unit dBm
    output["rssi"] = float(data[output["deveui"] + "-3"]["Signal strength"])
    # convert battery voltage to mV
    output["battery"] = float(data[output["deveui"] + "-4"]["battery"]) / (1*10**3)


def parse(package, sensor = "nb_100"):
	'''
    Gather essential info from package for reformatting
	'''
	data ={}
	try:
		data["deveui"] = package["nodeName"]
		data["time"] = package["time"]

		measurements = package["data"]
		for measurement in measurements:
			data[measurement["dataID"]] = {}

			for i in range(len(measurement["name"])):
				data[measurement["dataID"]][measurement["name"][i]] = measurement["value"][i]

	except (TypeError, IndexError, KeyError) as err:
		raise MeasurementTypeError("Unexpected packet") from err

	return reformat(data, sensor)


def reformat(data, sensor):
    '''
    Rebuild objects to unified form
    '''
    # Unique identification for each device
    output["deveui"] = data.pop("deveui")

    try:
        output["timestamp_parser"] = int(time())

        # convert nodes timestamp to unix epoch time
        time_parsed = datetime.datetime.strptime(data.pop("time"), "%Y-%m-%dT%H:%M:%S.%fZ")
        output["timestamp_node"] = int(time_parsed.replace(tzinfo=datetime.timezone.utc).timestamp())

    except ValueError:
            raise MeasurementTimestampError("Unexpected node timestamp") from err

    # nb-100 packets
    if sensor == "nb_100":
        nb_100(data)

    # aistin packets
    elif sensor == "aistin":
        # iterate trough measurements in the packet
        for measurement in data:
            aistin_measurements[measurement](data[measurement])

    print(json.dumps(output, indent=4, sort_keys=True))
    return output
            

aistin_measurements = {
    "B188": temperature_humidity,
    "B168": pressure,
    "B328": acceleration,
    "B228": battery,
    "B38C": orientation,
    "B1A9": motion,
    "B198": moisture,
    "B1E8": co2,
    "B1B8": total_movement,
    "B16C": differential_pressure,
    "B1EA": volatile_compounds,
    "B1D8": object_temperature,
    "B32A": amplitude_frequency
}
