from bottle import route, static_file
import json

import temperature, idle

@route('/all.json')
def sensor_json():
  try:
    return json.dumps({
      'temperature_events': temperature.get_events(),
      'idle_events': idle.get_events(),
    })
  except Exception as e:
    return e

@route('/idle.json')
def idle_json():
  try:
    return idle.get_json()
  except Exception as e:
    return e

@route('/idle/<id>.html')
def idle_id_txt(id):
  try:
    return idle.get_id_txt(id)
  except Exception as e:
    return e

@route('/all.html')
def sensor_html():
  try:
    return static_file('web/all.html', root='.')
  except Exception as e:
    return e

@route('/<filename>.js')
def javascript(filename):
  return static_file('web/%s.js' % filename, root='.')
