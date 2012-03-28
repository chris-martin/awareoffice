import sqlite3

def getCon():
  return sqlite3.connect('db.sqlite')

def init():

  con = getCon()

  con.cursor().execute('''
    create table if not exists tmp_event (
      ts text, id text, amb integer, tmp integer )''')

  con.cursor().execute('''
    create table if not exists idle_event (
      ts text, id text )''')

  con.commit()

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d
