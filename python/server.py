from bottle import get, post, static_file, request
import json

import temperature, idle

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

@get('/<filename>.html')
def html(filename):
  return static_file('web/%s.html' % filename, root='.')

@get('/<filename>.js')
def javascript(filename):
  return static_file('web/%s.js' % filename, root='.')

@get('/<filename>.css')
def html(filename):
  return static_file('web/%s.css' % filename, root='.')


@get('/images/<filename>')
def html(filename):
  return static_file('web/images/%s' % filename, root='.')

@post('/')
def update():
  print request.body.getvalue()
  data = json.loads(request.body.getvalue())
  temperature.save_many(data.get('tmp', []))
  idle.save_many(data.get('idle', []))
