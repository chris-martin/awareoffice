import time
import json
from urllib import urlopen

class Report:

  def __init__(self, remote):
    self.remote = remote
    self.empty()

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
      #try:
      urlopen(self.remote, json.dumps(self.data))
      #except :
      #  pass
      self.empty()

# an integer that changes every 2 seconds
def _now():
  return int(time.time() / 2)
