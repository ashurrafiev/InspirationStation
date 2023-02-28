import io
import json
from datetime import datetime, timedelta
import secrets

from jinja2 import Environment, FileSystemLoader
import cherrypy
import jwt


def load_auth_cfg():
    with io.open('auth.json') as f:
        return json.load(f)

def give_access_token(auth_cfg, user):
    now = datetime.now()
    with io.open('logins.txt', 'at') as log:
        agent = cherrypy.request.headers.get('User-Agent', None)
        print(f'{now}\t{user}\t{cherrypy.request.remote.ip}\tUser-Agent={agent}', file=log)

    token_data = {
        'sub': user,
        'exp': int(datetime.timestamp(now + timedelta(hours=auth_cfg.get('expire', 24))))
    }
    return jwt.encode(token_data, auth_cfg['jwtKey'], algorithm="HS256")

def check_password(auth_cfg, user, pwd):
    allow = user in auth_cfg['users']
    pwd_check = auth_cfg['users'].get(user, pwd)
    return secrets.compare_digest(pwd, pwd_check) and allow

def check_access_token(auth_cfg, token):
    if not token:
        return None
    try:
        token_data = jwt.decode(token, auth_cfg['jwtKey'], algorithms="HS256")
        user = token_data['sub']
        if user not in auth_cfg['users']:
            return None
        exp = datetime.fromtimestamp(int(token_data['exp']))
        if exp < datetime.now():
            return None
        return user
    except:
        return None

def auth_user():
    token = cherrypy.request.cookie['token'].value if 'token' in cherrypy.request.cookie.keys() else None
    user = check_access_token(load_auth_cfg(), token)
    if not user:
        raise cherrypy.HTTPRedirect(cherrypy.url('/login'))
    return user


class StoryMod(object):
    def __init__(self):
        self.tenv = Environment(
            loader=FileSystemLoader('template/storymod')
        )
        self.tenv.filters['app'] = cherrypy.url

    @cherrypy.expose
    def index(self):
        user = auth_user()
        cookie_data = dict()
        for name in cherrypy.request.cookie.keys():
            cookie_data[name] = cherrypy.request.cookie[name].value

        template = self.tenv.get_template("index.html")
        return template.render(user=user, cookies=json.dumps(cookie_data, indent=2))

    @cherrypy.expose
    def login(self, user='', pwd=''):
        auth_cfg = load_auth_cfg()
        if check_password(auth_cfg, user, pwd):
            cherrypy.response.cookie['token'] = give_access_token(auth_cfg, user)
            raise cherrypy.HTTPRedirect(cherrypy.url('/'))
        template = self.tenv.get_template("login.html")
        error = 'Wrong user or password.' if user else None
        return template.render(user=user, error=error)

    @cherrypy.expose
    def logout(self):
        cherrypy.response.cookie['token'] = ''
        cherrypy.response.cookie['token']['expires'] = 0
        cherrypy.response.cookie['token']['max-age'] = 0
        raise cherrypy.HTTPRedirect(cherrypy.url('/login'))
