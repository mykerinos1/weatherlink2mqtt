# weatherlink2mqtt

Get temperature, humidity values from https://www.weatherlink.com/ (Weatherlink) and send it to your MQTT broker

# Why ?

I did not find anything so I had to build it with python.

# Usage

## Prerequisite

You simply need Python3 (never tested with Python2.7) and the only dependencies are `requests` (to access the api) and `paho-mqtt` (for MQTT broker interaction) so this line should be enough  :

```bash
pip3 install paho-mqtt requests
```

## Getting your API token

You're on your own here, the documentation is strange.

## Using the script

Easy, first try a dry-run command :

```bash
./weatherlink2mqtt.py -a '<API_KEY>' -n -v
```

and then a real command to add to your crontab :

```bash
./weatherlink2mqtt.py -c '<CITY_ID>' -a '<API_KEY>'
```

The secrets can also be set with environment variables, see the help for more detail.

## Help

```bash
/ # weatherlink2mqtt.py --help
usage: weatherlink2mqtt.py [-h] -a WLAPIKEY [-m HOST] [-n]
                           [-o PREVIOUSFILENAME] [-t TOPIC] [-T TOPIC] [-v]

Read current temperature and humidity from Weatherlink and send them to a MQTT
broker.

optional arguments:
  -h, --help            show this help message and exit
  -a WLAPIKEY, --wl-api-key WLAPIKEY
                        Weatherlink API Key. (default: None)
  -m HOST, --mqtt-host HOST
                        Specify the MQTT host to connect to. (default:
                        127.0.0.1)
  -n, --dry-run         No data will be sent to the MQTT broker. (default:
                        False)
  -o PREVIOUSFILENAME, --last-time PREVIOUSFILENAME
                        The file where the last timestamp coming from
                        Weatherlink API will be saved (default: /tmp/wl_last)
  -t TOPIC, --topic TOPIC
                        The MQTT topic on which to publish the message (if it
                        was a success). (default: sensor/outdoor)
  -T TOPIC, --topic-error TOPIC
                        The MQTT topic on which to publish the message (if it
                        wasn't a success). (default: error/sensor/outdoor)
  -v, --verbose         Enable debug messages. (default: False)
```

## Other things to know

I personaly use cron to start this program so as I want to keep the latest timestamp received from the API, I store it by default in `/tmp/wl_last` (you can change it through a command line parameter).

## Docker

I added a sample Dockerfile, I personaly use it with a `docker-compose.yml` like this one :

```yml
version: '3'

services:
  weatherlink:
    build: https://github.com/seblucas/weatherlink2mqtt.git
    image: weatherlink2mqtt-python3-cron:latest
    restart: always
    environment:
      WEATHERLINK_API_KEY: YOUR_API_KEY
      CRON_STRINGS: "09 * * * * weatherlink2mqtt.py -m localhost -v"
      CRON_LOG_LEVEL: 8
```

# Limits

None, I hope at least ;). 

# License

This program is licenced with GNU GENERAL PUBLIC LICENSE version 3 by Free Software Foundation, Inc.
