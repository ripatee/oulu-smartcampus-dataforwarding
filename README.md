# HTTP to MQTT forwarder

HTTP to MQTT forwarder is a program to get IOT-data from HTTP post request, parse it to wanted format and send it to MQTT-broker. Software is developed to one specific purpose and enviroment only.

### Running

1. ´pip install -r requirements.txt´
2. ´cp settings.conf.example settings.conf´
3. ´python3 main.py´

### Testing

This project includes some unit-tests that can used in, for example developing support for new sensor types.

1. ´pip install -r requirements.txt´
2. ´python3 test.py´

### Todo

- Gracefully handle interrupted connection to MQTT-broker

### Licence

Copyright 2020 Risto Korhonen (ripatee) and Jeremias Körkkö under the MIT license.