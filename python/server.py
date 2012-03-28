from bottle import get, post, static_file, request
import json

import temperature, idle

@get('/all.json')
def all_json():
  return json.dumps({
    'temperature_events': temperature.get_events(),
    'idle_events': idle.get_events(),
  })

@get('/idle.json')
def idle_json():
  return idle.get_json()

@get('/idle/<id>.html')
def idle_id_txt(id):
  return idle.get_id_txt(id)

@get('/<filename>.html')
def html(filename):
  return static_file('web/%s.html' % filename, root='.')

@get('/<filename>.js')
def javascript(filename):
  return static_file('web/%s.js' % filename, root='.')

@get('/<filename>.css')
def html(filename):
  return static_file('web/%s.css' % filename, root='.')

@post('/')
def update():

  print request.body.getvalue()
  data = json.loads(request.body.getvalue())

  temperature.save_list(data.get('temperature_events', []))

  for e in data.get('idle_events', []):
    idle.save(
      id = e.sensor_id,
      timestamp = e.get('timestamp'),
    )
