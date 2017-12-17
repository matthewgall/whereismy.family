#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
import sys, requests

class Nominatim:
	def __init__(self):
		self.baseURL = "https://nominatim.openstreetmap.org"
		self.headers = {
			"User-Agent": "python/osm-nominatim"
		}

	def __parse__(self, data, respFormat):
		if respFormat is "json":
			return data.json()
		return data.text

	def __check__(self, lat, lon):
		# At a minimum, the app needs the latitude and longitude
		if not (lat or lon):
			return False

		# Latitude measures how far north or south of the equator a place is located. 
		# The equator is situated at 0°, the North Pole at 90° north (or 90°, because a positive 
		# latitude implies north), and the South Pole at 90° south (or -90°). Latitude measurements
		# range from 0° to (+/–)90°.
		if not (float(lat) <= -90) and (float(lat) >= 90):
			return False

		# Longitude measures how far east or west of the prime meridian a place is located.
		# The prime meridian runs through Greenwich, England. Longitude measurements range from 0° 
		# to (+/–)180°.
		if not (float(lon) <= -180) and (float(lon) >= 180):
			return False

		return True

	def search(self, query, addressDetails=1, respFormat="json"):
		payload = {
			'format': respFormat,
			'q': query,
			'addressdetails': addressDetails
		}
		data = requests.get('{}/search'.format(self.baseURL),
			headers=self.headers,
			params=payload
		)
		return self.__parse__(data, respFormat)

	def reverse(self, lat, lon, zoomLevel=14, addressDetails=1, respFormat="json"):
		if not self.__check__(lat, lon):
			raise ValueError

		payload = {
			'format': respFormat,
			'lat': lat,
			'lon': lon,
			'zoom': zoomLevel,
			'addressdetails': addressDetails
		}
		data = requests.get('{}/reverse'.format(self.baseURL),
			headers=self.headers,
			params=payload
		)
		return self.__parse__(data, respFormat)

if __name__ == '__main__':
	lookup = Nominatim()
	if sys.argv[1] == "reverse":
		print(lookup.reverse(sys.argv[2], sys.argv[3], sys.argv[4]))
	elif sys.argv[1] == "search":
		print(lookup.search(sys.argv[2]))