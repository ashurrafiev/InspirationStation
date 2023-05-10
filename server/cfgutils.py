import io
import os
import json
import re

from jinja2 import Environment, FileSystemLoader
import cherrypy


def load_config() -> dict:
    with io.open('config.json') as f:
        return json.load(f)

def load_blocked_words() -> dict:
    with io.open('blocked_words.txt') as f:
        words = set()
        for line in f:
            w = line.rstrip()
            if w: words.add(w)
        return words

def get_auth_cfg(cfg):
    return cfg['modAuth']

def load_object_data() -> dict:
    with io.open('static/object_data.json') as f:
        return json.load(f)

def pluralize(count, plural='s', singular=''):
    return singular if count == 1 else plural

def template_env(path='template'):
    env = Environment(loader=FileSystemLoader(path))
    env.filters['app'] = cherrypy.url

    env.filters['pl'] = pluralize
    return env

def check_uid(uid):
    return re.match(r"^[A-Fa-f0-9\-]{8,40}$", uid)

def check_int(x, fb, check=None):
    try:
        x = int(x)
        return x if check is None or check(x) else fb
    except (ValueError, TypeError):
        return fb

def tail(f, n=1, buf_size=1024):
    lines = []
    i = -1
    while len(lines) < n:
        try:
            f.seek(i * buf_size, os.SEEK_END)
        except IOError:
            f.seek(0)
            lines = f.readlines()
            break
        lines = f.readlines()
        i -= 1
    return lines[-n:]

def delete_cookie(name):
    cherrypy.response.cookie[name] = ''
    cherrypy.response.cookie[name]['expires'] = 0
    cherrypy.response.cookie[name]['max-age'] = 0
