import jinja2

class Render:
    def __init__(self, path:str='template'):
        self.tenv = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
        self.tenv.filters['time'] = lambda d : d.strftime('%A, %Y-%m-%d, %H:%M')
        self.tenv.filters['date'] = lambda d : d.strftime('%A, %Y-%m-%d')

    def print_t(self, template_name:str, **kwargs):
        print(self.tenv.get_template(template_name+'.html').render(kwargs))
        
    def begin_print(self, title:str):
        self.print_t('header', title=title)

    def end_print(self):
        print('</body></html>')
