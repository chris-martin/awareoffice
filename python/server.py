from bottle import get, post, static_file, request
import json

import temperature, idle, status

@get('/all.json')
def all_json():
  return json.dumps({
    'tmp': temperature.get_recent(10),
    'idle': idle.get_recent(10),
  })

@get('/idle.json')
def idle_json():
  return json.dumps({
    'events': idle.get_recent(5 * 60)
  })

@get('/status.json')
def status_json():
  return json.dumps(status.get_statuses())

@get('/<path:path>')
def mobile(path):
  return static_file('web/mobile/%s' % path, root='.')

@get('/')
def mobile_index():
  return mobile('index.html')

@post('/')
def update():
  data = json.loads(request.body.getvalue())
  temperature.save_many(data.get('tmp', []))
  idle.save_many(data.get('idle', []))
