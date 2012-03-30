import bottle
from socket import gethostname
import signal
import sys

import server, temperature, idle, status, purple, db
from report import Report

default_port = 8080
default_id = gethostname()

def start(id=default_id, remote=None, port=default_port, use_purple=False, dummy=False, central=False):
  db.init()
  report = Report(args.remote) if remote else None
  temperature.run(id, report, dummy=dummy)
  if use_purple: purple.run(id)
  if not dummy: idle.run(id, report)
  status.run(id)
  if central: bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=port)
  else: wait_for_interrupt()

def wait_for_interrupt():
  print 'Hit Ctrl-C to quit.'
  def signal_handler(signal, frame): sys.exit()
  signal.signal(signal.SIGINT, signal_handler)
  while True: signal.pause()

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('--port', default=default_port, help='the port number for this web server')
  parser.add_argument('--id', default=default_id, help='a string identifying the sensor')
  parser.add_argument('--remote', help='the url of the central server')
  parser.add_argument('--central', action='store_true', help='run this node as the central server')
  parser.add_argument('--purple', action='store_true', help='update jabber status')
  parser.add_argument('--dummy', action='store_true', help='generate random data instead of using sensors')
  args = parser.parse_args()
  start(id = args.id, remote = args.remote, port = args.port,
    use_purple = args.purple, dummy = args.dummy, central=args.central)
