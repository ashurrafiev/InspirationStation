import io
import os.path
from urllib.parse import quote as urlencode

import cherrypy
from cherrypy.lib import file_generator
import qrcode

from cfgutils import load_config, load_object_data, load_story_template, check_uid, template_env
from storymod import StoryMod
import storydb


class InspirationStation(object):
    def __init__(self):
        self.tenv = template_env()

    @cherrypy.expose
    def index(self):
        return ""

    @cherrypy.expose
    def story(self, uid='', obj='', q1='', q2='', q3=''):
        preview = uid == 'preview'
        if not preview and not check_uid(uid):
            raise cherrypy.HTTPError(404)
        cfg = load_config()

        story_cfg = load_story_template()
        if preview:
            data = {'obj': obj, 'q1': q1, 'q2': q2, 'q3': q3}
            message = ''
            link = ''
            blocked = False
        else:
            data = storydb.get_story(cfg, uid)
            if not data:
                raise cherrypy.HTTPError(404)
            blocked = (data['mod']=='block')
            message = urlencode(story_cfg['message'])
            link = f"{cfg['storyURL']}{uid}"

        obj = data['obj']
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(404)
        data['name'] = obj_data[obj]['name']
        data['fact'] = obj_data[obj]['fact']

        story_template = self.tenv.from_string(story_cfg['story'])
        template = self.tenv.get_template("story.html")
        return template.render(
            story_template=story_template,
            data=data,
            blocked=blocked,
            message=message,
            link=link
        )

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def post(self, obj='', q1='', q2='', q3=''):
        if not obj or not q1 or not q2 or not q3:
            raise cherrypy.HTTPError(400)
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(400)

        cfg = load_config()
        data = { 'obj': obj, 'q1': q1, 'q2': q2, 'q3': q3 }
        uid = storydb.post_story(cfg, user=None, ip=cherrypy.request.remote.ip, data=data)
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
