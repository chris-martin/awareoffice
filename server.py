import bottle, sqlite3, json

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

@bottle.route('/recent.json')
def recent():
  try:
    con = sqlite3.connect('sensorData.sqlite')
    con.row_factory = dict_factory
    c = con.cursor()
    c.execute("""select * from temperature_event
      where datetime(timestamp, 'unixepoch', '+10 seconds') > datetime('now')""")
    events = []
    for row in c:
      events.append(row)
    return json.dumps({ 'events': events })
  except Exception as e:
    return e

@bottle.route('/')
def index():
  try:
    return bottle.static_file('index.html', root='.')
  except Exception as e:
    return e

@bottle.route('/<filename>.js')
def index(filename):
  return bottle.static_file('%s.js' % filename, root='.')

bottle.run(host='inductance', port='8080')
