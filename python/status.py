import time
import db

def get_statuses(id=None):

  query = """
      select id, avg(tmp) as tmp from tmp_event
      where ts > :ts
    """
  params = { 'ts': int((time.time() - 5) * 1000) }
  if id is not None:
    query += " and id = :id"
    params['id'] = id

  query += """
      group by id
    """

  statuses = {}

  c = db.getCon().cursor()
  c.execute(query, params)
  for row in c:
    id = row['id']
    tmp = row['tmp']
    status = {
      'id': id,
      'tmp': tmp,
      'status': status_for_tmp(tmp)
    }
    statuses[id] = status

  return statuses

def status_for_tmp(tmp):
  return 'away' if tmp < 22.5 else 'available'

def get_status(id):
  return get_statuses(id).get(id)

