import sqlite3
from ctypes import *
import sys
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, TemperatureChangeEventArgs
from Phidgets.Devices.TemperatureSensor import TemperatureSensor, ThermocoupleType
from time import sleep

def getCon():
  return sqlite3.connect('sensorData.sqlite')

con = getCon()
con.cursor().execute('''create table if not exists temperature_event (
  timestamp    text,
  sensor_id    text,
  ambient      integer,
  temperature  integer )''')
con.commit()

sensor = TemperatureSensor()
sensor.openPhidget()
sensor.waitForAttach(2000)
sensorId = sensor.getSerialNum()
sensor.setTemperatureChangeTrigger(0, 0.1)

def onChange(e):
  print e.temperature
  con = getCon()
  con.cursor().execute("""insert into temperature_event
    values (strftime('%s', 'now'), ?, ?, ?)""",
    (sensorId, sensor.getAmbientTemperature(), e.temperature))
  con.commit()
sensor.setOnTemperatureChangeHandler(onChange)

sleep(5)
chr = sys.stdin.read(1)
sensor.closePhidget()
