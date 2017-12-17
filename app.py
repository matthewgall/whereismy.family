#!/usr/bin/env python

import os, sys, argparse, logging, json, base64, datetime
import requests, redis, humanize
from bottle import route, request, response, default_app, view, template, static_file, auth_basic, parse_auth

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
		r.set(username, json.dumps({
			'lat': data['lat'],
			'lon': data['lon'],
			'tid': data['tid'],
			'tst': data['tst']
		}))

	return json.dumps({
		'_type': 'card',
		'name': "@{}".format(username)
	})

@route('/<user>', ('GET'))
@route('/<user>.<ext>', ('GET'))
def get_user(user, ext='html'):
	data = json.loads(r.get(user))

	delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(int(data['tst']))
	data['delta'] = humanize.naturaltime(delta)

	if ext in ['json']:
		response.headers['Content-Type'] = 'application/json'
		return json.loads(data)
	return template('user', username=user, data=data)

@route('/', ('GET', 'POST'))
def index():
	return template("index")

if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	# Server settings
	parser.add_argument("-i", "--host", default=os.getenv('IP', '127.0.0.1'), help="server ip")
	parser.add_argument("-p", "--port", default=os.getenv('PORT', 5000), help="server port")

	# Redis settings
	parser.add_argument("--redis-host", default=os.getenv('REDIS_HOST', 'localhost'), help="redis hostname")
	parser.add_argument("--redis-port", default=os.getenv('REDIS_PORT', 6379), help="redis port")
	parser.add_argument("--redis-pw", default=os.getenv('REDIS_PW', ''), help="redis password")

	# Verbose mode
	parser.add_argument("--verbose", "-v", help="increase output verbosity", action="store_true")
	args = parser.parse_args()

	if args.verbose:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)
	log = logging.getLogger(__name__)

	try:
		r = redis.Redis(
			host=args.redis_host,
			port=args.redis_port, 
			password=args.redis_pw,
		)
	except:
		log.error("Unable to connect to redis on {}:{}".format(args.redis_host, args.redis_port))

	try:
		app = default_app()
		app.run(host=args.host, port=args.port, server='tornado')
	except:
		log.error("Unable to start server on {}:{}".format(args.host, args.port))