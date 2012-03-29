from threading import Thread
from time import sleep
import time
import os
import status

class PurpleThread ( Thread ):

  status_messages = {
    'away': 'Away',
    'available': 'Here'
  }

  def __init__(self, id):
    super(PurpleThread, self).__init__()
    self._halt = False
    self.id = id

  def run(self):
    while not self._halt:
      self.go()
      sleep(1)

  def go(self):
    s = status.get_status(self.id)
    if s is not None:
      message = self.status_messages[s['status']]
      os.system('purple-remote "setstatus?status=%s&message=%s (%.1f degrees celsius)"' % (s['status'], message, s['tmp']))

  def halt(self):
    self._halt = True
