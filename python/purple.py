from threading import Thread
from time import sleep
import os
import status

class PurpleThread ( Thread ):

  status_messages = {
    'away': 'Away from desk',
    'available': 'At desk'
  }

  last_status = None

  def __init__(self, id):
    super(PurpleThread, self).__init__()
    self.id = id

  def run(self):
    while True:
      self.go()
      sleep(1)

  def go(self):
    s = status.get(self.id)
    if s is not None and s['status'] != self.last_status:
      message = self.status_messages[s['status']]
      os.system('purple-remote "setstatus?status=%s&message=%s"' % (s['status'], message))

def run(*args, **kwargs):
  thread = PurpleThread(*args, **kwargs)
  thread.daemon = True
  thread.start()
