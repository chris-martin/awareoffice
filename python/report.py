import time
import json
from urllib import urlopen
from threading import Thread, Condition

class Report:

  def __init__(self, remote):
    self.remote = remote
    self.empty()
    self.thread = ReportingThread(remote)
    self.thread.start()

  def empty(self, now=None):
    self.now = now or _now()
    self.data = {
      'tmp': [],
      'idle': [],
    }

  def append(self, key, value):
    self.data[key].append(value)
    now = _now()
    if now != self.now:
      self.thread.condition.acquire()
      self.thread.data = json.dumps(self.data)
      self.thread.condition.notify()
      self.thread.condition.release()
      self.empty()

class ReportingThread ( Thread ):

  def __init__(self, remote):
    super(ReportingThread, self).__init__()
    self.condition = Condition()
    self.daemon = True
    self.remote = remote
    self.data = None

  def run(self):
    while True:
      self.condition.acquire()
      while self.data is None:
        self.condition.wait()
      try:
        urlopen(self.remote, self.data)
      except Exception:
        pass
      finally:
        self.data = None
        self.condition.release()

# an integer that changes every 2 seconds
def _now():
  return int(time.time() / 2)
