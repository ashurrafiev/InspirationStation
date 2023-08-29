import sys
from utils import cli
from utils.parselog import *
from utils.render import RenderHTML, write_csv

args = cli.parse_args()
log = cli.input_data(args)

event_defs = [
    ('SERVER_RECEIVE_LOG', None, 10, 'Interactive is online'),
    ('PULL_LEVER', None, 5, 'Lever pulled'),
    ('OPEN_OBJECT', None, 5, 'Object clicked'),
    ('ON_PAGE', None, 5, 'Editing or navigating story UI'),
    ('POST_STORY', None, 5, 'Story posted')
]
csv_bin = 5

def print_heatmap(r:RenderHTML, log, event:str, info_regex=None, bin:int=5, maxx:int=0, section=True, timeline=True, legend=True):
    if section:
        r.print_t('section', title=event, timespan=(log[0]['t'], log[-1]['t']))
    r.print_t('heatmap',
            heatmap=heatmap(filter_event(log, event, info_regex), bin),
            bin=bin, start_hour=6, end_hour=18,
            bin_size = bin, maxx=maxx, timeline=timeline, legend=legend
        )

def print_heatmap_set(r:RenderHTML, log, maxx, events):
    r.print('<table>')
    for i, (event, info_regex, bin, title) in enumerate(events):
        r.print(f'<tr><td style="text-align:right">{title} ({event})</td><td>')
        timeline = (i==0)
        legend = (i==len(events)-1)
        print_heatmap(r, log, event, info_regex=info_regex, bin=bin, maxx=maxx, section=False, timeline=timeline, legend=legend)
        r.print('</td></tr>')
    r.print('</table>')

if args.format=='.html':
    daily = split_daily(log)
    r = RenderHTML(output=args.output)
    title = 'Event heatmap'
    r.begin_print(title)
    r.print_t('section', title=title, timespan=(log[0]['t'], log[-1]['t']))
    print_heatmap_set(r, log, 10*len(daily), events=event_defs)
    r.print_t('section', title='Daily')
    for d in daily:
        r.print_t('section', date=d[0]['t'])
        print_heatmap_set(r, d, 30, events=event_defs)
    r.end_print()
elif args.format=='.csv':
    cols = ['t']
    heatmaps = dict()
    num_bins = 0
    for event, info_regex, _, title in event_defs:
        cols.append(title)
        hm = heatmap(filter_event(log, event, info_regex), bin=csv_bin)
        if not num_bins:
            num_bins = len(hm)
        heatmaps[event] = hm
    table = list()
    for i in range(0, num_bins):
        t = 360 + i*csv_bin
        row = [ f'{t//60:02d}:{t%60:02d}' ]
        for event, _, _, _ in event_defs:
            row.append(heatmaps[event][i])
        table.append(row)
    write_csv(table, output=args.output, cols=cols)
else:
    print('Unknown output format: '+args.format, file=sys.stderr)
