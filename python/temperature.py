from threading import Thread
from urllib import urlopen
import json

from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, TemperatureChangeEventArgs
from Phidgets.Devices.TemperatureSensor import TemperatureSensor, ThermocoupleType

import db

class SensorThread ( Thread ):

  def __init__(self, sensorId, remote=None):
    super(SensorThread, self).__init__()
    self.sensorId = sensorId
    self.remote = remote

  def run(self, sensorId=None):

    try:
      sensor = self.sensor = TemperatureSensor()
      sensor.openPhidget()
      sensor.waitForAttach(2000)
      if self.sensorId is None: self.sensorId = sensor.getSerialNum()
      sensor.setTemperatureChangeTrigger(0, 0.1)
      sensor.setOnTemperatureChangeHandler(self.onChange)
    except PhidgetException:
      print 'No temperature sensor detected.'

  def onChange(self, e):

    id = self.sensorId
    ambient = self.sensor.getAmbientTemperature()
    temperature = e.temperature
    save( id=id, ambient=ambient, temperature=temperature )
    if self.remote:
      urlopen(self.remote, json.dumps({'temperature_events': [{'sensor_id': id, 'ambient': ambient, 'temperature': temperature}]}))

def save(id, ambient, temperature, timestamp=None):

  con = db.getCon()

  if timestamp is None:
    con.cursor().execute("""
      insert into temperature_event values (strftime('%s', 'now'), ?, ?, ?)
    """, (id, ambient, temperature))
  else:
    con.cursor().execute("""
      insert into temperature_event values (?, ?, ?, ?)
    """, (timestamp, id, ambient, temperature))

  con.commit()

def get_events():

  con = db.getCon()
  con.row_factory = db.dict_factory
  c = con.cursor()
  c.execute("""
    select * from temperature_event
    where datetime(timestamp, 'unixepoch', '+10 seconds') > datetime('now')
  """)
  events = []
  for row in c:
    events.append(row)
  return events
