from threading import Thread
from time import sleep
import os

import gobject
import dbus
from dbus import glib

import status

class LockThread ( Thread ):

  last_status = None

  def __init__(self, id):
    super(LockThread, self).__init__()
    self.id = id

  def run(self):
    while True:
      self.go()
      sleep(1)

  def go(self):
    s = status.get(self.id)
    if s is 'away':
      lock()

# http://wiki.python.org/moin/DbusExamples
def lock():
  gobject.threads_init()
  glib.init_threads()
  bus = dbus.SessionBus()
  remote_object = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
  iface = dbus.Interface(remote_object, 'org.freedesktop.DBus')
  screensaver = bus.get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
  iface = dbus.Interface(screensaver, 'org.gnome.ScreenSaver')
  iface.Lock()

def run(*args, **kwargs):
  thread = LockThread(*args, **kwargs)
  thread.daemon = True
  thread.start()
