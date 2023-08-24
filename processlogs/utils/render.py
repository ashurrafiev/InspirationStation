import csv
import sys
import jinja2

def rgb(r:float, g:float, b:float) -> str:
    return f'#{round(r*255.0):02x}{round(g*255.0):02x}{round(b*255.0):02x}'

def heat_gradient(s:float) -> str:
    if s<0: s = 0
    if s>1: s = 1
    r = s*2.0 if s<0.5 else 1.0
    g = 0.0 if s<0.25 else (s-0.25)*2.0 if s<0.75 else 1.0
    b = 0.0 if s<0.5 else (s-0.5)*2.0
    return rgb(r, g, b)

def heat_gradient_i(x:int, maxx:int) -> str:
    s = 1 if x==0 else 0.75 - 0.75*(x/maxx)
    return heat_gradient(s)

class RenderHTML:
    def __init__(self, output:str=None, template_path:str='template'):
        self.out = open(output, 'w') if output else None
        self.tenv = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.tenv.filters['time'] = lambda d : d.strftime('%A, %Y-%m-%d, %H:%M')
        self.tenv.filters['date'] = lambda d : d.strftime('%A, %Y-%m-%d')
        self.tenv.globals['heat_gradient'] = heat_gradient
        self.tenv.globals['heat_gradient_i'] = heat_gradient_i

    def print(self, s:str):
        print(s, file=self.out)

    def print_t(self, template_name:str, **kwargs):
        print(self.tenv.get_template(template_name+'.html').render(kwargs), file=self.out)
        
    def begin_print(self, title:str):
        self.print_t('header', title=title)

    def end_print(self):
        self.print('</body></html>')

def write_csv(table, output:str=None, cols=None, totals=None):
    with (open(output, 'w') if output else sys.stdout) as f:
        out = csv.writer(f)
        if cols:
            out.writerow(cols)
        out.writerows(table)
        if totals:
            out.writerow(totals)
