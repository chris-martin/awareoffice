import commands
from threading import Thread
from time import sleep
import json

import db

class IdleThread ( Thread ):

  def __init__(self, sensorId, remote=None):
    super(IdleThread, self).__init__()
    self._halt = False
    self.sensorId = sensorId

  def run(self):
    while not self._halt:
      self.go()
      sleep(1)

  def idleMs(self):
    return int(commands.getoutput('python python/idle.py'))

  def go(self):
    if self.idleMs() < 2000:
      save(id = self.sensorId)

  def halt(self):
    self._halt = True

def save(id, timestamp=None):
  con = db.getCon()
  if timestamp is None:
    con.cursor().execute("""
      insert into idle_event
      values (strftime('%s', 'now'), ?)
    """, (id,))
  else:
    con.cursor().execute("""
      insert into idle_event
      values (?, ?)
    """, (timestamp, id,))
  con.commit()

def get_events():
  con = db.getCon()
  con.row_factory = db.dict_factory
  c = con.cursor()
  c.execute("""
    select * from idle_event
    where datetime(timestamp, 'unixepoch', '+10 seconds') > datetime('now')
  """)
  events = []
  for row in c:
    events.append(row)
  return events

def get_json():
  con = db.getCon()
  con.row_factory = db.dict_factory
  c = con.cursor()
  c.execute("""
    select * from idle_event
    where datetime(timestamp, 'unixepoch', '+5 minutes') > datetime('now')
  """)
  events = []
  for row in c:
    events.append(row)
  return json.dumps({ 'events': events })

def get_id_txt(id):
  con = db.getCon()
  c = con.cursor()
  c.execute("""
    select strftime('%H:%M:%S', datetime(timestamp, 'unixepoch', 'localtime')) from idle_event
    where datetime(timestamp, 'unixepoch', '+5 minutes') > datetime('now')
    and sensor_id = ? order by timestamp desc
  """, (id,))
  response = '<h1>Last five minutes of keyboard/mouse activity events for %s</h1><ul>' % id
  for row in c:
    response += '<li>%s</li>' % row[0]
  response += '</ul>'
  return response

# We run this script as a separate process because, for reasons unknown,
# it gives a segmentation fault when run by a sub-thread.

if __name__ == '__main__':

  import ctypes, os

  # https://gist.github.com/1879754
  class XScreenSaverInfo( ctypes.Structure):
    """ typedef struct { ... } XScreenSaverInfo; """
    _fields_ = [('window',      ctypes.c_ulong), # screen saver window
                ('state',       ctypes.c_int),   # off,on,disabled
                ('kind',        ctypes.c_int),   # blanked,internal,external
                ('since',       ctypes.c_ulong), # milliseconds
                ('idle',        ctypes.c_ulong), # milliseconds
                ('event_mask',  ctypes.c_ulong)] # events

  xlib = ctypes.cdll.LoadLibrary('libX11.so')
  display = xlib.XOpenDisplay(os.environ['DISPLAY'])
  xss = ctypes.cdll.LoadLibrary('libXss.so.1')
  xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
  xssinfo = xss.XScreenSaverAllocInfo()
  xss.XScreenSaverQueryInfo(display, xlib.XDefaultRootWindow(display), xssinfo)

  print "%d" % xssinfo.contents.idle
