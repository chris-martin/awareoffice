from argparse import ArgumentParser
import bottle, json
from socket import gethostname

import temperature, idle, purple, db

@bottle.route('/all.json')
def sensor_json():
  try:
    return json.dumps({
      'temperature_events': temperature.get_events(),
      'idle_events': idle.get_events(),
    })
  except Exception as e:
    return e

@bottle.route('/idle.json')
def idle_json():
  try:
    return idle.get_json()
  except Exception as e:
    return e

@bottle.route('/idle/<id>.html')
def idle_id_txt(id):
  try:
    return idle.get_id_txt(id)
  except Exception as e:
    return e

@bottle.route('/all.html')
def sensor_html():
  try:
    return bottle.static_file('web/all.html', root='.')
  except Exception as e:
    return e

@bottle.route('/<filename>.js')
def javascript(filename):
  return bottle.static_file('web/%s.js' % filename, root='.')

def parseArgs():
  parser = ArgumentParser()
  parser.add_argument('--http_host', default='localhost', help='the host name for this web server')
  parser.add_argument('--http_port', default='8080', help='the port number for this web server')
  parser.add_argument('--sensor_id', default=gethostname(), help='a string identifying the sensor')
  parser.add_argument('--aggregator', help='the url of the central server')
  return parser.parse_args()

args = parseArgs()
db.init()
temperature.SensorThread(args.sensor_id).start()
purple_thread = purple.PurpleThread(args.sensor_id)
purple_thread.start()
idle_thread = idle.IdleThread(args.sensor_id)
idle_thread.start()
bottle.run(host=args.http_host, port=args.http_port)
purple_thread.halt()
idle_thread.halt()
