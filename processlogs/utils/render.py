import csv
import sys
import jinja2

class RenderHTML:
    def __init__(self, output:str=None, template_path:str='template'):
        self.out = open(output, 'w') if output else None
        self.tenv = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.tenv.filters['time'] = lambda d : d.strftime('%A, %Y-%m-%d, %H:%M')
        self.tenv.filters['date'] = lambda d : d.strftime('%A, %Y-%m-%d')

    def print_t(self, template_name:str, **kwargs):
        print(self.tenv.get_template(template_name+'.html').render(kwargs), file=self.out)
        
    def begin_print(self, title:str):
        self.print_t('header', title=title)

    def end_print(self):
        print('</body></html>', file=self.out)

def write_csv(table, output:str=None, cols=None, totals=None):
    with (open(output, 'w') if output else sys.stdout) as f:
        out = csv.writer(f)
        if cols:
            out.writerow(cols)
        out.writerows(table)
        if totals:
            out.writerow(totals)
