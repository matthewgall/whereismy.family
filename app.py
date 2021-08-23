#!/usr/bin/env python

import os, sys, argparse, logging, json, base64, datetime, time, random, string
import requests, humanize, what3words, redis
from bottle import route, request, response, default_app, view, template, static_file, auth_basic, parse_auth
from haversine import haversine, Unit
from modules import Nominatim

def enable_cors(fn):
	def _enable_cors(*args, **kwargs):
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

		if request.method != 'OPTIONS':
			return fn(*args, **kwargs)
	return _enable_cors

def auth_user(user, password):
	return True

def get_user_location(user):
	redis_data = r.get("location/{}".format(user))
	if redis_data:
		return json.loads(redis_data)
	return None

@route('/static/<filepath:path>')
def static(filepath):
	return static_file(filepath, root='views/static')

@auth_basic(auth_user)
@route('/update', ('POST'))
def update():
	try:
		data = json.loads(request.body.read())
	except:
		return json.dumps({
			'success': False,
			'message': "We were unable to process your location update due to invalid data"
		})

	# Is this a location update?
	if data['_type'] in ['location']:
		username, password = parse_auth(request.headers.get('Authorization'))

		if not password is args.seed:
			return json.dumps({
				'success': False,
				'message': "You provided an incorrect password for updates"
			})

		# Now we check for the distance between their current location and their update
		prev = json.loads(r.get(f"location/{username}"))
		dist = haversine((prev['lat'], prev['lon']), (data['lat'], data['lon']), unit=Unit.METERS)

		if not dist > int(args.accept_accuracy):
			return json.dumps({
				'success': False,
				'message': "New location is less than 100m from previous location. Ignoring"
			})

		# Now we save this to redis
		r.set(f"location/{username}", json.dumps({
			'lat': data['lat'],
			'lon': data['lon'],
			'tid': data['tid'],
			'tst': data['tst']
		}))

	return json.dumps({
		'_type': 'card',
		'name': f"@{username}"
	})

@route('/<user>', ('GET'))
@route('/<user>.<ext>', ('GET'))
def get_user(user, ext='html'):
	if f"{user}.{ext}" in ['favicon.ico', "robots.txt"]:
		return ""

	data = get_user_location(user)
	if data == None:
		return template("error")

	delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(int(data['tst']))
	data['delta'] = humanize.naturaltime(delta)
	data['display_name'] = Nominatim().reverse(data['lat'], data['lon'], args.location_zoom)['display_name']

	if args.w3w != "":
		try:
			data['w3w'] = what3words.Geocoder(args.w3w).convert_to_3wa(what3words.Coordinates(data['lat'], data['lon']))['words']
		except:
			data['w3w'] = ''

	if ext in ['json']:
		response.headers['Content-Type'] = 'application/json'
		return json.dumps({
			"location": data
		})

	if ext in ['mapbox']:
		response.headers['Content-Type'] = 'application/json'
		body = {
			"type": "FeatureCollection",
			"features": [{
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [data['lon'], data['lat']]
				},
				"properties": {
					"title": data['display_name'],
					"description": data['delta']
				}
			}]
		}
		return json.dumps(body)
	return template(
		'user/index',
		args=args,
		data=data,
		username=user
	)

@route('/', ('GET', 'POST'))
def index():
	return template("index", args=args)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	# Server settings
	parser.add_argument("-i", "--host", default=os.getenv('IP', '127.0.0.1'), help="server ip")
	parser.add_argument("-p", "--port", default=os.getenv('PORT', 5000), help="server port")
	parser.add_argument("-s", "--seed", default=os.getenv('SEED', ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))), help="server seed")
	
	# Redis settings
	parser.add_argument("--redis", default=os.getenv('REDISTOGO_URL', os.getenv('REDIS', 'redis://localhost:6379/0')), help="redis connection string")

	# API tokens
	parser.add_argument("--mapbox", default=os.getenv('MAPBOX', ''), help="mapbox api token")
	parser.add_argument("--w3w", default=os.getenv('W3W', ''), help="what3words api token")

	# Application settings
	parser.add_argument("--enable-register", "-e", help="enable registration", action="store_true")

	# Location settings
	parser.add_argument("--accept-accuracy", default=os.getenv('ACC_ACCEPT', 100), help="locations under this level of accuracy will be accepted")
	
	# Zoom settings
	parser.add_argument("--location-zoom", default=os.getenv('LOCATION_ZOOM', 10), help="locations when displayed, will be displayed at this zoom level")
	parser.add_argument("--map-zoom", default=os.getenv('MAP_ZOOM', 14), help="locations when displayed, will be displayed at this zoom level")
	
	# Verbose mode
	parser.add_argument("--verbose", "-v", help="increase output verbosity", action="store_true")
	args = parser.parse_args()

	if args.verbose:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)
	log = logging.getLogger(__name__)

	try:
		r = redis.Redis().from_url(args.redis)
		r.set('test', 'test')
		t = r.get('test')
		r.delete('test')
	except:
		log.fatal(f"Unable to successfully connect to redis: {args.redis}")
		exit()

	try:
		print(f"Using secure seed: {args.seed}")
		app = default_app()
		app.run(host=args.host, port=args.port, server='tornado')
	except:
		log.error(f"Unable to start server on {args.host}:{args.port}")
		exit()
