from argparse import ArgumentParser
import bottle, sqlite3, json, sys, socket, os, ctypes, commands
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, TemperatureChangeEventArgs
from Phidgets.Devices.TemperatureSensor import TemperatureSensor, ThermocoupleType
from threading import Thread
from time import sleep

def getCon():
  return sqlite3.connect('db.sqlite')

def initDb():
  con = getCon()
  con.cursor().execute('''create table if not exists temperature_event (
    timestamp    text,
    sensor_id    text,
    ambient      integer,
    temperature  integer )''')
  con.cursor().execute('''create table if not exists idle_event (
    timestamp    text,
    sensor_id    text )''')
  con.commit()

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def get_temperature_events():
  con = getCon()
  con.row_factory = dict_factory
  c = con.cursor()
  c.execute("""select * from temperature_event
    where datetime(timestamp, 'unixepoch', '+10 seconds') > datetime('now')""")
  events = []
  for row in c:
    events.append(row)
  return events

def get_idle_events():
  con = getCon()
  con.row_factory = dict_factory
  c = con.cursor()
  c.execute("""select * from idle_event
    where datetime(timestamp, 'unixepoch', '+10 seconds') > datetime('now')""")
  events = []
  for row in c:
    events.append(row)
  return events

@bottle.route('/all.json')
def sensor_json():
  try:
    return json.dumps({
      'temperature_events': get_temperature_events(),
      'idle_events': get_idle_events(),
    })
  except Exception as e:
    return e

@bottle.route('/idle.json')
def idle_json():
  try:
    con = getCon()
    con.row_factory = dict_factory
    c = con.cursor()
    c.execute("""select * from idle_event
      where datetime(timestamp, 'unixepoch', '+5 minutes') > datetime('now')""")
    events = []
    for row in c:
      events.append(row)
    return json.dumps({ 'events': events })
  except Exception as e:
    return e

@bottle.route('/idle/<id>.html')
def idle_id_txt(id):
  try:
    con = getCon()
    c = con.cursor()
    c.execute("""select strftime('%H:%M:%S', datetime(timestamp, 'unixepoch', 'localtime')) from idle_event
      where datetime(timestamp, 'unixepoch', '+5 minutes') > datetime('now')
      and sensor_id = ? order by timestamp desc""",
      (id,))
    response = '<h1>Last five minutes of keyboard/mouse activity events for %s</h1><ul>' % id
    for row in c:
      response += '<li>%s</li>' % row[0]
    response += '</ul>'
    return response
  except Exception as e:
    return e

@bottle.route('/all.html')
def sensor_html():
  try:
    return bottle.static_file('web/all.html', root='.')
  except Exception as e:
    return e

@bottle.route('/<filename>.js')
def javascript(filename):
  return bottle.static_file('web/%s.js' % filename, root='.')

class SensorThread ( Thread ):

  def __init__(self, sensorId):
    super(SensorThread, self).__init__()
    self.sensorId = sensorId

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
    con = getCon()
    con.cursor().execute("""insert into temperature_event
      values (strftime('%s', 'now'), ?, ?, ?)""",
      (self.sensorId, self.sensor.getAmbientTemperature(), e.temperature))
    con.commit()

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
    con = getCon()
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

class IdleThread ( Thread ):

  def __init__(self, sensorId):
    super(IdleThread, self).__init__()
    self._halt = False
    self.sensorId = sensorId

  def run(self):
    while not self._halt:
      self.go()
      sleep(1)

  def idleMs(self):
    return int(commands.getoutput('python idle.py'))

  def go(self):
    if self.idleMs() < 2000:
      con = getCon()
      con.cursor().execute("""insert into idle_event
        values (strftime('%s', 'now'), ?)""",
        (self.sensorId,))
      con.commit()

  def halt(self):
    self._halt = True

def parseArgs():
  parser = ArgumentParser()
  parser.add_argument('--http_host', default='localhost', help='the host name for this web server')
  parser.add_argument('--http_port', default='8080', help='the port number for this web server')
  parser.add_argument('--sensor_id', default=socket.gethostname(), help='a string identifying the sensor')
  parser.add_argument('--aggregator', help='the url of the central server')
  return parser.parse_args()

args = parseArgs()
initDb()
SensorThread(args.sensor_id).start()
purple = PurpleThread(args.sensor_id)
purple.start()
idle = IdleThread(args.sensor_id)
idle.start()
bottle.run(host=args.http_host, port=args.http_port)
purple.halt()
idle.halt()
