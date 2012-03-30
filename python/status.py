import time
from time import sleep
from threading import Thread

import db, temperature, idle

def get(id=None):

  if id:
    st = _select_latest_status(id)
    if not st: return None
    idle_time = _select_latest_available_time(id)
    if idle_time: idle_time = time.time() * 1000 - idle_time
    return { 'status': st, 'idle_time': idle_time }

  return dict(map(lambda id: [id, get(id)], _select_recent_ids(15)))

def _select_latest_status(id):
  c = db.getCon().cursor()
  c.execute("""
    select status from status_event
    where id = ?
    order by ts desc limit 1
  """, (id,))
  row = c.fetchone()
  return row['status'] if row else None

def _select_latest_available_time(id):
  c = db.getCon().cursor()
  c.execute("""
    select ts from status_event
    where id = ? and status = 'available'
    order by ts desc limit 1
  """, (id,))
  row = c.fetchone()
  return row['ts'] if row else None

def _select_recent_ids(sec):
  c = db.getCon().cursor()
  c.execute("""
    select distinct id
    from status_event
    where ts > ?
  """, (int((time.time() - sec) * 1000),))
  return map(lambda row: row['id'], c)

def _is_available(id, tmp):
  if (idle.get_latest(id) or 0) > 1000 * (time.time() - 5): return True
  if tmp > 22.5: return True
  return False

def _status(*args, **kwargs):
  return 'available' if _is_available(*args, **kwargs) else 'away'

def _get(id=None):
  tmp = temperature.get_recent_avg(5, id)
  if id: return _status(id, tmp)
  return dict(map(lambda (id, tmp): [id, _status(id, tmp)], tmp.iteritems()))

class StatusThread ( Thread ):

  def __init__(self, id):
    super(StatusThread, self).__init__()
    self.id = id

  def run(self):
    while True:
      self.go()
      sleep(2)

  def go(self):
    now = int(time.time() * 1000)
    values = map(lambda (id, status): { 'ts': now, 'id': id, 'status': status }, _get().iteritems())
    con = db.getCon()
    con.cursor().executemany("""
      insert into status_event
      values (:ts, :id, :status)
    """, values)
    con.commit()

def run(*args, **kwargs):
  thread = StatusThread(*args, **kwargs)
  thread.daemon = True
  thread.start()
