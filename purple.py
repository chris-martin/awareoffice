import sqlite3
from time import sleep
import os

def go():
  con = sqlite3.connect('sensorData.sqlite')
  c = con.cursor()
  c.execute("""select temperature from temperature_event
    where datetime(timestamp, 'unixepoch', '+5 seconds') > datetime('now')""")
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

while True:
  go()
  sleep(1)
