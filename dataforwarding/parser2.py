from time import time
import datetime
from enum import Enum as enum


class MeasurementTimestampError(Exception):
    pass

class MeasurementTypeError(Exception):
    pass

class Sensor(enum):
    nb_100 = 1
    aistin = 2


def temperature_humidity(data):
    '''
    Temp in Celcius degrees,
    humidity in %
    '''
    temperature = round(float(data["temperature"]), 1)
    humidity = round(float(data["humidity"]), 1)
    return {"temperature": temperature, "humidity": humidity}


def pressure(data):
    '''
    Pressure in Bars
    '''
    return {"pressure": float(data["pressure"] / (1*10**3))}


def acceleration(data):
    '''
    Convert each axis to G
    '''
    acceleration_ = {}
    acceleration_["x"] = int(data["X-axis"]) / (1*10**3)
    acceleration_["y"] = int(data["Y-axis"]) / (1*10**3)
    acceleration_["z"] = int(data["Z-axis"]) / (1*10**3)
    return {"acceleration": acceleration_}


def battery(data):
    '''
    Voltage converted to mV, percentage in %
    '''
    battery_voltage = float(data["battery voltage"]) / (1*10**3)
    battery_percentage = round(float(data["battery"]))
    return {"battery": battery_voltage,
            "battery_percentage": battery_percentage}


def orientation(data):
    '''
    Offset from horizontal level(top up) in degrees
    '''
    return {"orientation": float(data["orientation"])}

def motion(data):
    '''
    timeframes = lenght of measurement period in seconds
    motions = Amount of registered movements inside the time period
    output["motion"] = average amount of motions per 15 mins
    '''
    timeframes = data["period"] / 900
    motions = data["movement"]
    return {"motion": int(motions / timeframes)}


def moisture(data):
    '''
    Given in relative humidity RH%
    '''
    return {"moisture": float(data["moisture"])}


def co2(data):
    '''
    Given in parts per million
    '''
    return {"co2": int(data["carbon dioxide"])}


def total_movement(data):
    '''
    Total movements registered since boot
    '''
    return {"total_movement": int(data["count"])}


def differential_pressure(data):
    '''
    Difference in pressure of two areas.
    Given in Pascals for lower resolution.
    '''
    return {"differential_pressure": float(data["pressure"])}


def volatile_compounds(data):
    '''
    Given in parts per billion
    '''
    return {"organic_compounds": int(data["Total Volatile Organic Compounds"])}


def object_temperature(data):
    '''
    Object temperature in Celcius degrees
    '''
    return {"object_temperature": float(data["temperature"])}


def amplitude_frequency(data):
    '''
    amplitude in mm, frequency in Hz
    '''
    return {"amplitude": int(data["amplitude"]),
            "frequency": int(data["frequency"])}


def nb_100(data, deveui):
    '''
    reformat nb_100 data
    '''
    output = {}
    temperature_humidity_parsed = temperature_humidity(data[deveui + "-1"])
    output.update(temperature_humidity_parsed)
    # convert pressure to Bars
    # NOTE! received value is not in mBars as suggested.
    output["pressure"] = round(float(data[deveui + "-2"]["pressure"]) / (1*10**5), 3)
    # unit dBm
    output["rssi"] = float(data[deveui + "-3"]["Signal strength"])
    # convert battery voltage to mV
    output["battery"] = float(data[deveui + "-4"]["battery"]) / (1*10**3)
    
    return output


def parse(package, sensor=Sensor.nb_100):
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
    output = {}
    # Unique identification for each device
    output["deveui"] = data.pop("deveui")

    try:
        output["timestamp_parser"] = int(time())

        # convert nodes timestamp to unix epoch time
        time_parsed = datetime.datetime.strptime(data.pop("time"), "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp_node = int(time_parsed.replace(tzinfo=datetime.timezone.utc).timestamp())
        output["timestamp_node"] = timestamp_node

    except ValueError:
        raise MeasurementTimestampError("Unexpected node timestamp") from err

    # nb-100 packets
    if sensor == Sensor.nb_100:
        parsed_data = nb_100(data, output["deveui"])
        output.update(parsed_data)

    # aistin packets
    elif sensor == Sensor.aistin:

        for measurement in data:
            parsed_data = aistin_measurements[measurement](data[measurement])
            output.update(parsed_data)

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
