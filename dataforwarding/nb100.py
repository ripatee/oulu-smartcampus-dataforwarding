import datetime
import time

def parse(package):  # Received data from sensor
    try:
        output = {}
        # Pick index of value and place it in output
        output["deveui"] = package["deviceName"]
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
