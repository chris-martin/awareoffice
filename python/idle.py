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
  save_many([{ 'id': id, 'ts': int(time.time() * 1000) }])

def save_many(list):
  con = db.getCon()
  con.cursor().executemany("""
    insert into idle_event
    values (:ts, :id)
  """, list)
  con.commit()

# retrieves all idle events from the past [sec] seconds
def get_recent(sec):
  con = db.getCon()
  con.row_factory = db.dict_factory
  c = con.cursor()
  c.execute("""
    select * from idle_event
    where ts > ? order by ts desc
  """, (
    int((time.time() - sec) * 1000),
  ))
  events = []
  for row in c:
    events.append(row)
  return events

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
