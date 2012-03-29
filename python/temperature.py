from threading import Thread
from urllib import urlopen
import json
import time

from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.TemperatureSensor import TemperatureSensor

import db

class SensorThread ( Thread ):

  def __init__(self, id=None, remote=None):
    super(SensorThread, self).__init__()
    self.id = id
    self.remote = remote
    if self.remote:
      self.remote_backlog = []
      self.remote_time = self.now()

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

  def onChange(self, e):
    x = {
      'id': self.id,
      'amb': self.sensor.getAmbientTemperature(),
      'tmp': e.temperature,
      'ts': int(time.time() * 1000),
    }
    save_many([x])
    if self.remote:
      self.remote_backlog.append(x)
      self.clear_backlog()

  def clear_backlog(self):
    now = self.now()
    if now != self.remote_time:
      urlopen(self.remote, json.dumps({ 'tmp': self.remote_backlog }))
      self.remote_time = self.now()
      self.remote_backlog = []

  # an integer that changes every 2 seconds
  def now(self):
    return int(time.time() / 2)

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
