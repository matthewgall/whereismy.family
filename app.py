#!/usr/bin/env python

import os, sys, argparse, logging, json, base64, datetime, time
import requests, redis, humanize, what3words
from bottle import route, request, response, default_app, view, template, static_file, auth_basic, parse_auth
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage
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
		if db.get(where('username') == user):
			if db.get(where('username') == user)['expires'] <= int(time.time()):
				return json.loads(db.get(where('username') == user)['data'])
			else:
				db.remove(where('username') == user)

		# Then redis
		redis_data = r.get("location/{}".format(user))
		if redis_data:
			# Then we put it in memory
			db.insert({
				'username': user,
				'data': r.get("location/{}".format(user)),
				'expires': int(time.time()) + int(args.redis_ttl)
			})

			# And return that
			return json.loads(db.get(where('username') == user)['data'])
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

		# Now we save this to redis
		r.set("location/{}".format(username), json.dumps({
			'lat': data['lat'],
			'lon': data['lon'],
			'tid': data['tid'],
			'tst': data['tst']
		}))

		# And delete our in memory representation
		db.remove(where('username') == username)

	return json.dumps({
		'_type': 'card',
		'name': "@{}".format(username)
	})

@route('/<user>', ('GET'))
@route('/<user>.<ext>', ('GET'))
def get_user(user, ext='html'):
	if "{}.{}".format(user, ext) in ['favicon.ico', "robots.txt"]:
		return ""

	data = get_user_location(user)
	delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(int(data['tst']))
	data['delta'] = humanize.naturaltime(delta)
	data['display_name'] = Nominatim().reverse(data['lat'], data['lon'], args.location_zoom)['display_name']

	if ext in ['json']:
		response.headers['Content-Type'] = 'application/json'
		return json.dumps(data)

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
					"title": "",
					"description": ""
				}
			}]
		}
		return json.dumps(body)
	return template(
		'user',
		args=args,
		data=data,
		username=user,
		w3w=what3words.Geocoder(args.w3w_token).reverse(lat=data['lat'], lng=data['lon'])['words']
	)

@route('/', ('GET', 'POST'))
def index():
	return template("index", args=args)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	# Server settings
	parser.add_argument("-i", "--host", default=os.getenv('IP', '127.0.0.1'), help="server ip")
	parser.add_argument("-p", "--port", default=os.getenv('PORT', 5000), help="server port")

	# Redis settings
	parser.add_argument("--redis-host", default=os.getenv('REDIS_HOST', 'localhost'), help="redis hostname")
	parser.add_argument("--redis-port", default=os.getenv('REDIS_PORT', 6379), help="redis port")
	parser.add_argument("--redis-pw", default=os.getenv('REDIS_PW', ''), help="redis password")
	parser.add_argument("--redis-ttl", default=os.getenv('REDIS_TTL', 604800), help="redis time to cache records")

	# API tokens
	parser.add_argument("--mapbox-token", default=os.getenv('MAPBOX_KEY', ''), help="mapbox api token")
	parser.add_argument("--w3w-token", default=os.getenv('W3W_KEY', ''), help="what3words api token")

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
		if os.getenv('REDISCLOUD_URL'):
			r = redis.from_url(os.getenv('REDISCLOUD_URL'))
		else:
			r = redis.Redis(
				host=args.redis_host,
				port=args.redis_port, 
				password=args.redis_pw,
			)
	except:
		log.fatal("Unable to connect to redis on {}:{}".format(args.redis_host, args.redis_port))
		exit()

	try:
		db = TinyDB(storage=MemoryStorage)
	except:
		log.fatal("Unable to connect to TinyDB")
		exit()

	try:
		app = default_app()
		app.run(host=args.host, port=args.port, server='tornado')
	except:
		log.error("Unable to start server on {}:{}".format(args.host, args.port))
		exit()