from threading import Thread
from time import sleep
import os
import status

class PurpleThread ( Thread ):

  status_messages = {
    'away': 'Away',
    'available': 'Here'
  }

  def __init__(self, id):
    super(PurpleThread, self).__init__()
    self.id = id

  def run(self):
    while True:
      self.go()
      sleep(1)

  def go(self):
    s = status.get_status(self.id)
    if s is not None:
      message = self.status_messages[s['status']]
      os.system('purple-remote "setstatus?status=%s&message=%s (%.1f degrees celsius)"' % (s['status'], message, s['tmp']))

def run(*args, **kwargs):
  thread = PurpleThread(*args, **kwargs)
  thread.daemon = True
  thread.start()
