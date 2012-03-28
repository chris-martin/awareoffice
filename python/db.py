import sqlite3

def getCon():
  return sqlite3.connect('db.sqlite')

def init():
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
