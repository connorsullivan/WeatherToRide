#!/usr/bin/python3

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/WeatherToRide/")

from WeatherToRide import app as application
