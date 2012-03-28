from argparse import ArgumentParser
import bottle
from socket import gethostname

import server, temperature, idle, purple, db

def parseArgs():
  parser = ArgumentParser()
  parser.add_argument('--host', default='localhost', help='the host name for this web server')
  parser.add_argument('--port', default='8080', help='the port number for this web server')
  parser.add_argument('--id', default=gethostname(), help='a string identifying the sensor')
  parser.add_argument('--remote', help='the url of the central server')
  return parser.parse_args()

args = parseArgs()
db.init()
temperature.SensorThread(sensorId = args.id, remote = args.remote).start()
purple_thread = purple.PurpleThread(sensorId = args.id)
purple_thread.start()
idle_thread = idle.IdleThread(sensorId = args.id, remote = args.remote)
idle_thread.start()
bottle.run(host=args.host, port=args.port)
purple_thread.halt()
idle_thread.halt()
