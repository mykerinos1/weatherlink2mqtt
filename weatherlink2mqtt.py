#!/usr/bin/env python3
#
#  weatherlink2mqtt.py
#
#  Copyright 2018 Sébastien Lucas <sebastien@slucas.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


import os, re, time, json, argparse
import requests                     # pip install requests
import paho.mqtt.publish as publish # pip install paho-mqtt

wlLastDt = None
verbose = False
WEATHERLINK_URL = 'https://www.weatherlink.com/embeddablePage/getData/{0}'

def debug(msg):
  if verbose:
    print (msg + "\n")

def environ_or_required(key):
  if os.environ.get(key):
    return {'default': os.environ.get(key)}
  else:
    return {'required': True}

def getWeatherlink(apiKey):
  global wlLastDt
  tstamp = int(time.time())
  wlUrl = WEATHERLINK_URL.format(apiKey)
  firefox_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

  debug ("Trying to get data from {0}".format(wlUrl))
  try:
    r = requests.get(wlUrl, headers=firefox_headers)
    data = r.json()
    if not 'lastReceived' in data:
      return (False, {"time": tstamp, "message": "Weatherlink data not well formed", "data": data})
    newObject = {"time": data['lastReceived'] // 1000, "temp": float(data['temperature']), "hum": int(round(float(data['humidity']))), "pres": float(data['barometer'])}
    return (True, newObject)
  except requests.exceptions.RequestException as e:
    return (False, {"time": tstamp, "message": "Weatherlink not available : " + str(e)})


parser = argparse.ArgumentParser(description='Read current temperature and humidity from Weatherlink and send them to a MQTT broker.',
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-a', '--wl-api-key', dest='wlApiKey', action="store",
                   help='Weatherlink API Key.',
                   **environ_or_required('WEATHERLINK_API_KEY'))
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-o', '--last-time', dest='previousFilename', action="store", default="/tmp/wl_last",
                   help='The file where the last timestamp coming from Weatherlink API will be saved')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/outdoor",
                   help='The MQTT topic on which to publish the message (if it was a success).')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/sensor/outdoor", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')


args = parser.parse_args()
verbose = args.verbose

status, data = getWeatherlink(args.wlApiKey)
jsonString = json.dumps(data)
if status:
  debug("Success with message <{0}>".format(jsonString))
  if os.path.isfile(args.previousFilename):
    oldTimestamp = open(args.previousFilename).read(10)
    if int(oldTimestamp) >= data["time"]:
      print ("No new data found")
      exit(0)

  # save the last timestamp in a file
  with open(args.previousFilename, 'w') as f:
    f.write(str(data["time"]))
  if not args.dryRun:
    publish.single(args.topic, jsonString, hostname=args.host)
else:
  debug("Failure with message <{0}>".format(jsonString))
  if not args.dryRun:
    publish.single(args.topicError, jsonString, hostname=args.host)

