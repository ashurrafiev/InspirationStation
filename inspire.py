import io
import json
import os.path
import re
from urllib.parse import quote as urlencode

from jinja2 import Environment, FileSystemLoader
import cherrypy
from cherrypy.lib import file_generator
import qrcode

from storymod import StoryMod
import storydb


def load_config() -> dict:
    with io.open('config.json') as f:
        return json.load(f)

def load_object_data() -> dict:
    with io.open('object_data.json') as f:
        return json.load(f)

def check_uid(uid):
    return re.match(r"^[A-Fa-f0-9\-]{8,40}$", uid)


class InspirationStation(object):
    def __init__(self):
        self.tenv = Environment(
            loader=FileSystemLoader('template')
        )

    @cherrypy.expose
    def index(self):
        return ""

    @cherrypy.expose
    def story(self, uid=''):
        if not check_uid(uid):
            raise cherrypy.HTTPError(404)
        cfg = load_config()
        data = storydb.get_story(cfg, uid)
        if not data:
            raise cherrypy.HTTPError(404)

        obj = data['obj']
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(404)
        data['name'] = obj_data[obj]['name']
        data['fact'] = obj_data[obj]['fact']

        template = self.tenv.get_template("story.html")
        message = urlencode(cfg['socialMediaMessage'])
        return template.render(json=json.dumps(data), message=message, link=f"{cfg['storyURL']}{uid}")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def post(self, obj='', q1='', q2='', q3=''):
        if not obj or not q1 or not q2 or not q3:
            raise cherrypy.HTTPError(400)
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(400)

        cfg = load_config()
        uid = storydb.post_story(cfg, data={ 'obj': obj, 'q1': q1, 'q2': q2, 'q3': q3 })
        return {
            'uid': uid,
            'story': cfg['storyURL'] + uid,
            'qr': '/qr/' + uid
        }

    @cherrypy.expose
    def qr(self, uid=''):
        cfg = load_config()
        if not check_uid(uid):
            raise cherrypy.HTTPError(400)
        img = qrcode.make(cfg['storyURL'] + uid)
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)
        cherrypy.response.headers['Content-Type'] = "image/png"
        return file_generator(buffer)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static',
            'tools.expires.on' : True,
            'tools.expires.secs' : 3600
        },
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './media',
            'tools.expires.on' : True,
            'tools.expires.secs' : 86400
        }
    }
    mod_conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'request.show_tracebacks': True # False
    })
    cherrypy.tree.mount(InspirationStation(), '/', conf)
    cherrypy.tree.mount(StoryMod(), '/storymod', mod_conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
