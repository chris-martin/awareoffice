from argparse import ArgumentParser
import bottle
from socket import gethostname

import server, temperature, idle, purple, db
from report import Report

def parseArgs():
  parser = ArgumentParser()
  parser.add_argument('--port', default='8080', help='the port number for this web server')
  parser.add_argument('--id', default=gethostname(), help='a string identifying the sensor')
  parser.add_argument('--remote', help='the url of the central server')
  return parser.parse_args()

args = parseArgs()
db.init()
report = Report(args.remote) if args.remote else None
id = args.id

try:
  temperature.start(id, report)
  purple.start(id)
  idle.start(id, report)
  bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=args.port)

finally:
  purple.stop()
  idle.stop()
