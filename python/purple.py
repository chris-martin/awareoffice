from threading import Thread
from time import sleep
import time
import os

import db

class PurpleThread ( Thread ):

  def __init__(self, id):
    super(PurpleThread, self).__init__()
    self._halt = False
    self.id = id

  def run(self):
    while not self._halt:
      self.go()
      sleep(1)

  def go(self):
    con = db.getCon()
    c = con.cursor()
    c.execute("""
      select tmp from tmp_event
      where ts > ? and id = ?
    """, (
      int((time.time() - 5) * 1000), self.id),
    )
    count = 0
    sum = 0
    for row in c:
      count += 1
      sum += float(row[0])
    if count:
      avg = sum / count
      if avg < 22.5:
        status = 'away'
        message = 'Away'
      else:
        status = 'available'
        message = 'Here'
      os.system('purple-remote "setstatus?status=%s&message=%s (%.1f degrees celcius)"' % (status, message, avg))

  def halt(self):
    self._halt = True
