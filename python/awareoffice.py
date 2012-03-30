import bottle
from socket import gethostname

import server, temperature, idle, status, purple, db
from report import Report

default_port = 8080
default_id = gethostname()

def start(id=default_id, remote=None, port=default_port):
  db.init()
  report = Report(args.remote) if remote else None
  temperature.run(id, report)
  purple.run(id)
  idle.run(id, report)
  status.run(id)
  bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=port)

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('--port', default=default_port, help='the port number for this web server')
  parser.add_argument('--id', default=default_id, help='a string identifying the sensor')
  parser.add_argument('--remote', help='the url of the central server')
  args = parser.parse_args()
  start(id = args.id, remote = args.remote, port = args.port)
