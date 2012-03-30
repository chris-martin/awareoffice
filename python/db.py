import sqlite3
import threading

_con_attr = 'awareoffice_db_connection'

def init():

  con = getCon()
  c = con.cursor()

  # ts : milliseconds utc
  # id : the sensor/machine/user id name

  # temperatures are stored as degrees celsius times 100
  # tmp : temperature
  # amb : ambient temperature

  c.execute('''
    create table if not exists tmp_event (
      ts integer, id text, amb real, tmp real )''')

  c.execute('''
    create table if not exists idle_event (
      ts integer, id text )''')

  c.execute('''
    create table if not exists status_event (
      ts integer, id text, status text )''')

  con.commit()

def _dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def getCon():

  local = threading.local()

  if not hasattr(local, _con_attr):
    con = sqlite3.connect('db.sqlite')
    con.row_factory = _dict_factory
    setattr(local, _con_attr, con)

  return getattr(local, _con_attr)
