import io
import os
from datetime import datetime
import urllib

import cherrypy
from cherrypy.lib import file_generator

class MediaProxy(object):
    @cherrypy.expose
    def index(self):
        return ""

    @cherrypy.expose
    def media(self, file=''):
        if not file:
            raise cherrypy.HTTPError(404)
            
        dl = False
        path = os.path.join(CACHE_PATH, file)
        cached = os.path.isfile(path)
        content_type = 'image/jpeg' if file.endswith('.jpg') else 'video/webm' if file.endswith('.webm') else False
            
        try:
            response = urllib.request.urlopen(os.path.join(CLOUD_URL, file), timeout=1)
            time = datetime.strptime(response.getheader('Last-Modified'), "%a, %d %b %Y %X %Z")
            cache_time = datetime.fromtimestamp(0)
            if cached:
                cache_time = datetime.fromtimestamp(os.path.getmtime(path))
            if cache_time < time:
                dl = True
                data = response.read()
                with io.open(path, 'wb') as f:
                    f.write(data)
            content_type = response.getheader('Content-Type')
        except:
            pass
        
        if not dl:
            if cached and content_type:
                with io.open(path, 'rb') as f:
                    data = f.read()
            else:
                raise cherrypy.HTTPError(404)
        
        cherrypy.response.headers['Content-Type'] = content_type
        buffer = io.BytesIO()
        buffer.write(data)
        buffer.seek(0)
        return file_generator(buffer)
            

if __name__ == '__main__':
    CLOUD_URL = os.environ['CLOUD_URL'] # must be set! otherwise will raise KeyError
    CACHE_PATH = os.environ.get('CACHE_PATH', './cache/')
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8088,
        'request.show_tracebacks': True
    })
    cherrypy.tree.mount(MediaProxy(), '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
