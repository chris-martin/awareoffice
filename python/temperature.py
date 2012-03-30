from threading import Thread
import time
import sys

from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.TemperatureSensor import TemperatureSensor

import db

class TmpThread ( Thread ):

  def __init__(self, id=None, report=None):
    super(TmpThread, self).__init__()
    self.id = id
    self.report = report

  def run(self):

    try:
      sensor = self.sensor = TemperatureSensor()
      sensor.openPhidget()
      sensor.waitForAttach(2000)
      if self.id is None: self.id = sensor.getSerialNum()
      sensor.setTemperatureChangeTrigger(0, 0.1)
      sensor.setOnTemperatureChangeHandler(self.onChange)
      print 'Temperature sensor detected.'
    except PhidgetException:
      print 'No temperature sensor detected.'
    except Exception:
      print 'Temperature sensor detection failed. Is the Phidgets library not installed?'

  def onChange(self, e):
    x = {
      'id': self.id,
      'amb': self.sensor.getAmbientTemperature(),
      'tmp': e.temperature,
      'ts': int(time.time() * 1000),
    }
    save_many([x])
    if self.report: self.report.append('tmp', x)

def save_many(list):

  con = db.getCon()

  con.cursor().executemany("""
    insert into tmp_event
    values (:ts, :id, :amb, :tmp)
  """, list)

  con.commit()

def get_recent(sec):

  c = db.getCon().cursor()
  c.execute("""
    select * from tmp_event
    where ts > ? order by ts desc
  """, (
    int((time.time() - sec) * 1000),
  ))
  events = []
  for row in c: events.append(row)
  return events

def run(*args, **kwargs):
  thread = TmpThread(*args, **kwargs)
  thread.daemon = True
  thread.start()
