from argparse import ArgumentParser
import bottle
from socket import gethostname

import server, temperature, idle, purple, db

def parseArgs():
  parser = ArgumentParser()
  parser.add_argument('--http_host', default='localhost', help='the host name for this web server')
  parser.add_argument('--http_port', default='8080', help='the port number for this web server')
  parser.add_argument('--sensor_id', default=gethostname(), help='a string identifying the sensor')
  parser.add_argument('--remote', help='the url of the central server')
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
