from threading import Thread
from time import sleep
import os

import db

class PurpleThread ( Thread ):

  def __init__(self, sensorId):
    super(PurpleThread, self).__init__()
    self._halt = False
    self.sensorId = sensorId

  def run(self):
    while not self._halt:
      self.go()
      sleep(1)

  def go(self):
    con = db.getCon()
    c = con.cursor()
    c.execute("""select temperature from temperature_event
      where datetime(timestamp, 'unixepoch', '+5 seconds') > datetime('now')
        and sensor_id = ?""", (self.sensorId,))
    count = 0
    sum = 0
    for row in c:
      count += 1
      sum = sum + float(row[0])
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
