from bottle import route, static_file
import json

import temperature, idle

@route('/all.json')
def sensor_json():
  return json.dumps({
    'temperature_events': temperature.get_events(),
    'idle_events': idle.get_events(),
  })

@route('/idle.json')
def idle_json():
  return idle.get_json()

@route('/idle/<id>.html')
def idle_id_txt(id):
  return idle.get_id_txt(id)

@route('/<filename>.html')
def html(filename):
  return static_file('web/%s.html' % filename, root='.')

@route('/<filename>.js')
def javascript(filename):
  return static_file('web/%s.js' % filename, root='.')

@route('/<filename>.css')
def html(filename):
  return static_file('web/%s.css' % filename, root='.')
