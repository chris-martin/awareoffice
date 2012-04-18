from threading import Thread
from time import sleep
import os

import gobject
import dbus
from dbus import glib

import status

class LockThread ( Thread ):

  last_status = None
  count = 0

  def __init__(self, id):
    super(LockThread, self).__init__()
    self.id = id

  def run(self):
    while True:
      self.go()
      sleep(1)

  def go(self):
    s = status.get(self.id)
    self.count = self.count + 1 if s['status'] == 'away' else 0
    lock(self.count > 2)

# http://wiki.python.org/moin/DbusExamples
def lock(x):
  gobject.threads_init()
  glib.init_threads()
  bus = dbus.SessionBus()
  screensaver = bus.get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
  iface = dbus.Interface(screensaver, 'org.gnome.ScreenSaver')
  iface.SetActive(x)

def run(*args, **kwargs):
  thread = LockThread(*args, **kwargs)
  thread.daemon = True
  thread.start()
