from threading import Thread
import time
from time import sleep
from random import Random

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

class DummyThread ( Thread ):

  def __init__(self, id=None, report=None):
    super(DummyThread, self).__init__()
    self.id = id
    self.report = report
    self.random = Random()
    self.random.seed()
    self.seedoffset = int(self.random.random() * 1000)

  def run(self):
    while True:
      self.onChange()
      sleep(.2)

  def onChange(self):
    x = {
      'id': self.id,
      'amb': 25,
      'tmp': self.tmp(),
      'ts': int(time.time() * 1000),
    }
    if self.report: self.report.append('tmp', x)

  def tmp(self):
    self.random.seed(self.seedoffset + int(time.time() / 5))
    x = self.random.randint(20, 25)
    self.random.seed()
    return x + ((self.random.random() - 0.5) * 6)

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

def get_recent_avg(sec, id=None):
  c = db.getCon().cursor()
  c.execute("""
    select id, avg(tmp) as tmp from tmp_event
    where ts > :ts %s
    group by id
  """ % ("and id = :id" if id else ""), {
    'ts': int((time.time() - 5) * 1000),
    'id': id
  })

  if id:
    row = c.fetchone()
    return row['tmp'] if row else None

  return dict(map(lambda row: [row['id'], row['tmp']], c))

def run(*args, **kwargs):
  dummy = kwargs['dummy']
  del kwargs['dummy']
  cls = DummyThread if dummy else TmpThread
  thread = cls(*args, **kwargs)
  thread.daemon = True
  thread.start()
