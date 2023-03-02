import io
from datetime import datetime, timedelta, timezone
import secrets

from jinja2 import Environment, FileSystemLoader
import cherrypy
import jwt

from cfgutils import load_config, load_object_data, get_auth_cfg, tail, check_int
import storydb

def create_access_token(auth_cfg, user):
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)
    with io.open('logins.txt', 'at') as log:
        agent = cherrypy.request.headers.get('User-Agent', None)
        if len(agent)>100:
            agent = agent[:100] + '...'
        print(f'{now}\t{user}\t{cherrypy.request.remote.ip}\t{agent}', file=log)

    token_data = {
        'sub': user,
        'exp': now + timedelta(hours=auth_cfg.get('expire', 24))
    }
    return jwt.encode(token_data, auth_cfg['jwtKey'], algorithm="HS256")

def give_access_token(auth_cfg, user):
    cherrypy.response.cookie['token'] = create_access_token(auth_cfg, user)
    cherrypy.response.cookie['token']['httponly'] = True
    # cherrypy.response.cookie['token']['secure'] = True

def check_password(auth_cfg, user, pwd):
    allow = user in auth_cfg['users']
    pwd_check = auth_cfg['users'].get(user, pwd)
    return secrets.compare_digest(pwd, pwd_check) and allow

def check_access_token(auth_cfg, token, refresh=True):
    if not token:
        return None, None
    try:
        token_data = jwt.decode(token, auth_cfg['jwtKey'], algorithms="HS256",
            options={'require': ['exp', 'sub']})
        user = token_data['sub']
        if user not in auth_cfg['users']:
            return None, None

        exp = datetime.fromtimestamp(token_data['exp'], tz=timezone.utc)
        if refresh and 'refresh' in auth_cfg:
            now = datetime.now(tz=timezone.utc)
            if now > exp - timedelta(hours=auth_cfg['refresh']):
                give_access_token(auth_cfg, user)

        return user, exp
    except jwt.InvalidTokenError:
        return None, None

def auth_user(cfg=None):
    token = cherrypy.request.cookie['token'].value if 'token' in cherrypy.request.cookie.keys() else None
    auth_cfg = get_auth_cfg(cfg if cfg else load_config())
    user, exp = check_access_token(auth_cfg, token)
    if not user:
        raise cherrypy.HTTPRedirect(cherrypy.url('/login'))
    return user, exp


class StoryMod(object):
    def __init__(self):
        self.tenv = Environment(
            loader=FileSystemLoader('template/storymod')
        )
        self.tenv.filters['app'] = cherrypy.url

    @cherrypy.expose
    def index(self, show=None, p=0, lim=20):
        cfg = load_config()
        user, _ = auth_user()

        p = check_int(p, 0, lambda x: x>=0)
        lim = check_int(lim, 20, lambda x: 5<=x<=100)

        if show and type(show) is str:
            show = [show]
        if show:
            show = [s for s in show if s in storydb.mod_options()]
        if not show:
            show = storydb.mod_options()

        obj_data = load_object_data()
        stories = storydb.list_stories(cfg, p, lim, sel=show)

        template = self.tenv.get_template("index.html")
        return template.render(
            user=user,
            stories=stories,
            obj_data=obj_data,
            show=show,
            page=p,
            lim=lim
        )

    @cherrypy.expose
    def recentlogins(self):
        user, exp = auth_user()

        with io.open('logins.txt') as f:
            logins = tail(f, 10)
        logins = [s.split('\t', 4) for s in logins]

        template = self.tenv.get_template("recentlogins.html")
        return template.render(user=user, expires=exp, logins=logins)

    @cherrypy.expose
    def login(self, user='', pwd=''):
        auth_cfg = get_auth_cfg(load_config())
        if check_password(auth_cfg, user, pwd):
            give_access_token(auth_cfg, user)
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
