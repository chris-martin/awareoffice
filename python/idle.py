import commands
from threading import Thread
from time import sleep
import time
import json

import db

class IdleThread ( Thread ):

  def __init__(self, id, remote=None):
    super(IdleThread, self).__init__()
    self._halt = False
    self.id = id

  def run(self):
    while not self._halt:
      if isActive(): save_now(self.id)
      sleep(1)

  def halt(self):
    self._halt = True

def isActive():
  return idleMs() < 2000

def idleMs():
  return int(commands.getoutput('python python/idle.py'))

def save_now(id):
  save_many([{ 'id': id, 'ts': int(time.time()) }])

def save_many(list):
  con = db.getCon()
  con.cursor().executemany("insert into idle_event values (:ts, :id)", list)
  con.commit()

# retrieves all idle events from the past [range] amount of time
def get_recent(range):
  con = db.getCon()
  con.row_factory = db.dict_factory
  c = con.cursor()
  c.execute("""
    select * from idle_event
    where datetime(ts, 'unixepoch', ?) > datetime(?)
    order by ts desc
  """, (range, int(time.time())))
  events = []
  for row in c:
    events.append(row)
  return events

def get_id_txt(id):
  con = db.getCon()
  c = con.cursor()
  c.execute("""
    select strftime('%H:%M:%S', datetime(ts, 'unixepoch', 'localtime')) from idle_event
    where datetime(ts, 'unixepoch', '+5 minutes') > datetime(?)
    and id = ? order by ts desc
  """, (id, int(time.time())))
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
