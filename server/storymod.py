import io
import json
import csv
import zipfile
from datetime import datetime, timedelta, timezone
import secrets

import cherrypy
from cherrypy.lib import file_generator
import jwt

from cfgutils import load_config, load_object_data,\
    get_auth_cfg, tail, check_int, delete_cookie, check_uid, template_env
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
        self.tenv = template_env('template/storymod')

    @cherrypy.expose
    def index(self, show=None, p=0, lim=None):
        cfg = load_config()
        user, _ = auth_user(cfg)

        # validating p
        p = check_int(p, 0, lambda x: x>=0)

        # validating lim, set cookie
        lim_fb = 20
        if 'lim' in cherrypy.request.cookie:
            lim_fb = check_int(cherrypy.request.cookie['lim'].value, lim_fb)
        lim = check_int(lim, lim_fb, lambda x: 5<=x<=100)
        cherrypy.response.cookie['lim'] = lim
        cherrypy.response.cookie['lim']['SameSite'] = 'Strict'

        # validating show, set cookie
        mod_options = storydb.mod_options()
        if show and type(show) is str:
            show = [show]
        if not show and 'show' in cherrypy.request.cookie:
            show = cherrypy.request.cookie['show'].value.split('+')
        if show:
            show = [s for s in show if s in mod_options]
        if not show:
            show = mod_options
        cherrypy.response.cookie['show'] = '+'.join(show)
        cherrypy.response.cookie['show']['SameSite'] = 'Strict'

        obj_data = load_object_data()
        counts, stories = storydb.list_stories(cfg, sel=show, p=p, lim=lim)
        total_pages = (int(counts['sel'])+lim-1) // lim

        template = self.tenv.get_template("index.html")
        return template.render(
            user=user,
            stories=stories,
            obj_data=obj_data,
            show=show,
            mod_options=mod_options,
            counts=counts,
            page=p,
            total_pages=total_pages,
            lim=lim
        )

    @cherrypy.expose
    def objects(self):
        cfg = load_config()
        user, _ = auth_user(cfg)
        obj_data = load_object_data()
        template = self.tenv.get_template("objects.html")
        return template.render(
            user=user,
            obj_data=obj_data
        )

    @cherrypy.expose
    def downloads(self):
        cfg = load_config()
        user, _ = auth_user(cfg)
        template = self.tenv.get_template("downloads.html")
        return template.render(user=user)
        
    @cherrypy.expose
    def data(self, req='', fmt=''):
        cfg = load_config()
        user, _ = auth_user(cfg)

        def send(cols, rows):
            if fmt=='json':
                buffer = json.dumps(storydb.assoc_rows(cols, rows), indent=2)
            elif fmt=='csv':
                out = io.StringIO()
                writer = csv.writer(out, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(cols)
                writer.writerows(rows)
                buffer = out.getvalue()
            else:
                raise cherrypy.HTTPError(400)

            now = int(datetime.now(tz=timezone.utc).timestamp())
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, allowZip64=False) as zip_file:
                zip_file.writestr(f'{req}{now}.{fmt}', buffer)

            cherrypy.response.headers['Content-Type'] = 'application/zip'
            cherrypy.response.headers['Content-Disposition'] = f'attachment; filename="{req}{now}.{fmt}.zip"'
            zip_buffer.seek(0)
            return file_generator(zip_buffer)

        if req=='stories':
            _, rows = storydb.list_stories(cfg, storydb.mod_options(), p=0, lim=1000000)
            rows = storydb.isoformat_time(rows)
            return send(['uid', 'obj', 'q1', 'q2', 'q3', 'time', 'mod', 'ip', 'editor', 'upd_time'], rows)
        elif req=='objects':
            obj_data = load_object_data()
            cols = ['id', 'name', 'fact', 'collectionNumber']
            def unzip(cols, id, obj):
                return [ id if c == 'id' else obj.get(c, None) for c in cols ]
            rows = [ unzip(cols, id, obj) for id, obj in obj_data.items() ]
            return send(cols, rows)
        else:
            raise cherrypy.HTTPError(400)

    @cherrypy.expose
    def edit(self, uid='new', p=0):
        cfg = load_config()
        user, _ = auth_user(cfg)

        new = uid == 'new'
        if not new and not check_uid(uid):
            raise cherrypy.HTTPError(400)
        if not new:
            story=storydb.get_story_raw(cfg, uid)
        else:
            story = [None, None, '', '', '', None, 'new']
        obj_data = load_object_data()

        template = self.tenv.get_template("edit.html")
        return template.render(
            user=user,
            story=story,
            obj_data=obj_data,
            mod_options=storydb.mod_options(),
            next_page=p
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
        delete_cookie('token')
        delete_cookie('lim')
        delete_cookie('show')
        raise cherrypy.HTTPRedirect(cherrypy.url('/login'))

    @cherrypy.expose
    def poststory(self, uid='new', p=0, obj='', q1='', q2='', q3='', status=''):
        cfg = load_config()
        user, _ = auth_user(cfg)

        new = uid == 'new'
        if not new and not check_uid(uid):
            raise cherrypy.HTTPError(400)
        if not obj or not q1 or not q2 or not q3:
            raise cherrypy.HTTPError(400)
        obj_data = load_object_data()
        if obj not in obj_data:
            raise cherrypy.HTTPError(400)
        if status not in storydb.mod_options():
           raise cherrypy.HTTPError(400)

        data = {'obj': obj, 'q1': q1, 'q2': q2, 'q3': q3, 'mod': status}
        if new:
            storydb.post_story(cfg, user, cherrypy.request.remote.ip, data)
        else:
            storydb.update_story(cfg, uid, user, data)

        raise cherrypy.HTTPRedirect(cherrypy.url('/edit?uid=new' if p=='new' else '/?p='+str(p)))

    @cherrypy.expose
    def setmod(self, sel='', status='', p=0, fetch=False):
        cfg = load_config()
        user, _ = auth_user(cfg)

        if not sel or status not in storydb.mod_options():
           raise cherrypy.HTTPError(400)
        sel = sel.split('+')

        if fetch:
            story = storydb.set_mod(cfg, sel[:1], user, status)
            obj_data = load_object_data()
            template = self.tenv.get_template("storyblk.html")
            return template.render(
                story=story,
                obj_data=obj_data,
                mod_options=storydb.mod_options()
            )
        else:
            # validating p
            p = check_int(p, 0, lambda x: x >= 0)
            storydb.set_mod(cfg, sel, user, status)
            raise cherrypy.HTTPRedirect(cherrypy.url('/?p='+str(p)))
