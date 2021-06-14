from time import time
import datetime


class MeasurementTimestampError(Exception):
    pass

class MeasurementTypeError(Exception):
    pass


def parse(package, sensor="nb_100"):
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
    Reformat data into compatible form
    New measurements marked with "#######"-comment
    '''
    try:
        output = {}
        # Unique identification for each device
        output["deveui"] = data["deveui"]

        try:
            output["timestamp_parser"] = int(time())

            # convert nodes timestamp to unix epoch time
            time_parsed = datetime.datetime.strptime(data["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
            output["timestamp_node"] = int(time_parsed.replace(tzinfo=datetime.timezone.utc).timestamp())

        except ValueError:
                raise MeasurementTimestampError("Unexpected node timestamp") from err

        # nb-100 packets
        if sensor == "nb_100":
            output["temperature"], output["humidity"] = temp_and_humi(data[output["deveui"] + "-1"])
            # convert pressure to Bars
            # NOTE! received value is not in mBars as suggested.
            output["pressure"] = round(float(data[output["deveui"] + "-2"]["pressure"]) / (1*10**5), 3)
            # unit dBm
            output["rssi"] = float(data[output["deveui"] + "-3"]["Signal strength"])
            # convert battery voltage to mV
            output["battery"] = float(data[output["deveui"] + "-4"]["battery"]) / (1*10**3)

        # aistin packets
            
        # Measurements can vary between devices, checks each measurement -
        # individually to maximize supported devices
        elif sensor == "aistin":
            if "B188" in data:
                output["temperature"], output["humidity"] = temp_and_humi(data["B188"])
            if "B168" in data:
                # convert pressure to bars
                output["pressure"] = float(data["B168"]["pressure"]) / (1*10**3)
            if "B328" in data:
                # Convert to G
                output["acceleration"] = {}
                output["acceleration"]["x"] = int(data["B328"]["X-axis"]) / (1*10**3)
                output["acceleration"]["y"] = int(data["B328"]["Y-axis"]) / (1*10**3)
                output["acceleration"]["z"] = int(data["B328"]["Z-axis"]) / (1*10**3)
            if "B228" in data:
                # Voltage converted to mV, percentage in %
                output["battery"] = float(data["B228"]["battery voltage"]) / (1*10**3)
                output["battery_percentage"] = float(data["B228"]["battery"]) #########
            if "B38C" in data:
                # Offset from horizontal level in degrees
                output["orientation"] = round(float(data["B38C"]["orientation"])) #########
            if "B1A9" in data:
                # timeframes = lenght of measurement period in seconds
                # motions = Amount of registered movements inside the time period
                # output["motion"] = average amount of motions per 15 mins
                timeframes = data["B1A9"]["period"] / 900
                motions = data["B1A9"]["movement"]
                output["motion"] = int(motions / timeframes)
            if "B198" in data:
                # Given in relative huimdity RH%
                output["moisture"] = float(data["B198"]["moisture"])
            if "B1E8" in data:
                # Given in parts per million
                output["co2"] = int(data["B1E8"]["carbon dioxide"])
            if "B1B8" in data:
                # Total movements since boot
                output["total_movement"] = int(data["B1B8"]["count"]) #######
            if "B16C" in data:
                # Difference in pressure of two areas
                # Given in Pascals for lower resolution
                output["differential_pressure"] = float(data["B16C"]["pressure"]) #####
            if "B1EA" in data:
                # Given in parts per billion
                output["organic_compounds"] = int(data["B1EA"]["Total Volatile Organic Compounds"]) ######
            if "B1D8" in data:
                # Object temperature in Celcius degrees
                output["object_temperature"] = float(data["B1D8"]["temperature"]) ######
            if "B32A" in data:
                # amplitue in mm, freq in Hz
                output["amplitude"] = int(data["B32A"]["amplitude"]) #########
                output["frequency"] = int(data["B32A"]["frequency"]) #########
        
    except (TypeError, IndexError, KeyError, ValueError) as err:
        raise MeasurementTypeError("Unexpected packet") from err

    return(output)


def temp_and_humi(data):
    '''
    Temp in Celcius degrees,
    humidity in %
    '''
    temp = round(float(data["temperature"]), 1)
    humi = round(float(data["humidity"]), 1)
    return temp, humi
