import io
import json
import os.path
import re
from urllib.parse import quote as urlencode

from psycopg2 import connect
from psycopg2 import Error as PostgresError

from jinja2 import Environment, FileSystemLoader
import cherrypy
from cherrypy.lib import file_generator
import qrcode

def load_config() -> dict:
    with io.open('config.json') as f:
        return json.load(f)

def load_object_data() -> dict:
    with io.open('object_data.json') as f:
        return json.load(f)

def check_uid(uid):
    if not re.match(r"^[A-Fa-f0-9\-]{8,40}$", uid):
        raise cherrypy.HTTPError(400)

def db_connect(cfg):
    db = cfg['database']
    return connect(
        host=db['host'],
        port=db.get('port', 5432),
        user=db.get('user', 'root'),
        password=db.get('pwd', ''),
        database=db['name']
    )

def db_post_story(cfg, data):
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO "stories" ("uid", "obj", "q1", "q2", "q3", "time")
                    VALUES (gen_random_uuid(), %(obj)s, %(q1)s, %(q2)s, %(q3)s, now())
                    RETURNING "uid"
                """, data)
                row = cursor.fetchone()
                connection.commit()
                return row[0] if row else None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def db_get_story(cfg, uid):
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT "obj", "q1", "q2", "q3",
                        extract(epoch from "time")::integer
                    FROM "stories"
                    WHERE "uid"=%s
                """, (uid,))
                row = cursor.fetchone()
                if row:
                    return dict(zip(['obj', 'q1', 'q2', 'q3', 'time'], row))
                else:
                    return None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

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
        check_uid(uid)
        cfg = load_config()
        data = db_get_story(cfg, uid)
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
        uid = db_post_story(cfg, data={ 'obj': obj, 'q1': q1, 'q2': q2, 'q3': q3 })
        return {
            'uid': uid,
            'story': cfg['storyURL'] + uid,
            'qr': '/qr/' + uid
        }

    @cherrypy.expose
    def qr(self, uid=''):
        cfg = load_config()
        check_uid(uid)
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
            'tools.staticdir.dir': './static'
        },
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './media'
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'request.show_tracebacks': False
    })
    cherrypy.quickstart(InspirationStation(), '/', conf)
