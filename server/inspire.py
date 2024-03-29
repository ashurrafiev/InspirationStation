import io
import pathlib
import re
import os.path
from datetime import datetime, timezone

import cherrypy
from cherrypy.lib import file_generator
import qrcode

from cfgutils import load_config, load_word_set, load_object_data, check_uid, template_env
from storymod import StoryMod
import storydb


class InspirationStation(object):
    def __init__(self):
        self.tenv = template_env()
        self.blocked_words = load_word_set('blocked_words.txt')
        self.known_words = load_word_set('known_words.txt')

    def contains_profanity(self, text):
        if not self.blocked_words or not self.known_words:
            return False
        word_count = 0
        unknown_words = 0
        # split words strippig down punctuation at the end of each word
        for w in re.split(r"[^A-Za-z]*(?:\s+|$)", text):
            if not w: # word had no letters, skip
                continue
            word_count += 1
            w = w.lower()
            if w in self.blocked_words:
                return True
            # words in known_words.txt are cropped to 8 letters max
            if w[:8] not in self.known_words:
                unknown_words += 1
                if unknown_words>5: # if over 5 unknown words, block rightaway
                    return True
        # block if no words with letters or too many unknown words
        return word_count==0 or (unknown_words/word_count)>0.5

    @cherrypy.expose
    def index(self):
        with open('static/index.html', 'rt') as f:
            return f.read()

    @cherrypy.expose
    def story(self, uid='', obj='', q1='', q2='', q3=''):
        preview = uid == 'preview'
        if not preview and not check_uid(uid):
            raise cherrypy.HTTPError(404)
        cfg = load_config()

        if preview:
            data = {'obj': obj, 'q1': q1, 'q2': q2, 'q3': q3}
            link = ''
            blocked = False
        else:
            data = storydb.get_story(cfg, uid)
            if not data:
                raise cherrypy.HTTPError(404)
            blocked = (data['mod']=='block')
            link = f"{cfg['storyURL']}{uid}"

        obj = data['obj']
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(404)
        data['name'] = obj_data[obj]['name']
        data['fact'] = obj_data[obj]['fact']

        template = self.tenv.get_template("story.html")
        return template.render(
            data=data,
            blocked=blocked,
            link=link
        )

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def post(self, obj='', q1='', q2='', q3=''):
        if not obj or not q1 or not q2 or not q3:
            raise cherrypy.HTTPError(400)
        if len(q1)>100 or len(q2)>100 or len(q3)>100:
            raise cherrypy.HTTPError(400)
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(400)
        if self.contains_profanity(' '.join([q1, q2, q3])):
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
    @cherrypy.tools.json_out()
    def postlog(self, log='', e=''):
        if not e:
            raise cherrypy.HTTPError(400)
        # empty log is expected to have e=1
        if e!='1' and not log:
            raise cherrypy.HTTPError(400)
        now = datetime.now(tz=timezone.utc)
        pathlib.Path('logs').mkdir(exist_ok=True)
        path = os.path.join('logs', now.strftime("station-%Y-%m")+'.txt')
        with open(path, 'a') as f:
            if log:
                print(log, file=f)
            t = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            header = f'{t}\tSERVER_RECEIVE_LOG\tip={cherrypy.request.remote.ip}'
            if e=='1':
                header += ',empty'
            print(header, file=f)
        return { 'res': 'OK' }
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def showcase(self, rand=''):
        cfg = load_config()
        _, rows = storydb.list_stories(cfg, ['star'], random_order=(rand=='1'))
        stories = [{'uid': r[0], 'obj': r[1], 'q1': r[2], 'q2': r[3], 'q3': r[4]} for r in rows]
        return stories

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


def start_server():
    cfg = load_config()
    global_conf = {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'log.error_file': cfg.get('errorLog', None),
    } if cfg.get('devMode', False) else {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'engine.autoreload.on': False,
        'checker.on': False,
        'tools.log_headers.on': False,
        'request.show_tracebacks': False,
        'request.show_mismatched_params': False,
        'log.screen': False,
        'tools.proxy.on': True
    }
    cherrypy.config.update(global_conf)
    
    root_path = os.path.abspath(os.getcwd())
    conf = {
        '/': {
            'tools.staticdir.root': root_path
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static',
            'tools.expires.on' : True,
            'tools.expires.secs' : 3600
        },
        '/favicon.ico': {        
            'tools.staticfile.on': True,        
            'tools.staticfile.filename': root_path+'/static/favicon.ico',
        }
    }
    if cfg.get('hostMedia', False):
        conf['/media'] = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': cfg['hostMedia'],
            'tools.expires.on' : True,
            'tools.expires.secs' : 86400
        }
    cherrypy.tree.mount(InspirationStation(), '/', conf)

    cherrypy.tree.mount(StoryMod(), '/storymod', {
        '/': {
            'tools.staticdir.root': root_path
        }
    })
    
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    start_server()
