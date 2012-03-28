from argparse import ArgumentParser
import bottle
from socket import gethostname

import server, temperature, idle, purple, db

def parseArgs():
  parser = ArgumentParser()
  parser.add_argument('--port', default='8080', help='the port number for this web server')
  parser.add_argument('--id', default=gethostname(), help='a string identifying the sensor')
  parser.add_argument('--remote', help='the url of the central server')
  return parser.parse_args()

args = parseArgs()

db.init()

tmp_thread = temperature.SensorThread(id = args.id, remote = args.remote)
tmp_thread.start()

purple_thread = purple.PurpleThread(id = args.id)
purple_thread.start()

idle_thread = idle.IdleThread(id = args.id, remote = args.remote)
idle_thread.start()

bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=args.port)

purple_thread.halt()

idle_thread.halt()
