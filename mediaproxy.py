import io
import os.path
from datetime import datetime
import urllib

import cherrypy
from cherrypy.lib import file_generator

CLOUD_URL = 'https://storyweb.ams3.cdn.digitaloceanspaces.com/'
CACHE_PATH = 'cache/'

class MediaProxy(object):
    @cherrypy.expose
    def index(self):
        return ""

    @cherrypy.expose
    def media(self, file=''):
        if not file:
            raise cherrypy.HTTPError(404)
        try:
            response = urllib.request.urlopen(CLOUD_URL+file)
        except urllib.error.HTTPError:
            raise cherrypy.HTTPError(404)
        
        time = datetime.strptime(response.getheader('Last-Modified'), "%a, %d %b %Y %X %Z")
        
        dl = False
        path = CACHE_PATH+file
        cache_time = datetime.fromtimestamp(0)
        if os.path.isfile(path):
            cache_time = datetime.fromtimestamp(os.path.getmtime(path))
        if cache_time < time:
            dl = True
            data = response.read()
            with io.open(path, 'wb') as f:
                f.write(data)
        else:
            with io.open(path, 'rb') as f:
                data = f.read()
        
        cherrypy.response.headers['Content-Type'] = response.getheader('Content-Type')
        buffer = io.BytesIO()
        buffer.write(data)
        buffer.seek(0)
        return file_generator(buffer)
            

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8088,
        'request.show_tracebacks': True
    })
    cherrypy.tree.mount(MediaProxy(), '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
