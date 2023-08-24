import sys
from utils import cli
from utils.parselog import *
from utils.render import RenderHTML

args = cli.parse_args()
log = cli.input_data(args)

def print_heatmap(r:RenderHTML, log, event:str, info_regex=None, bin:int=5, maxx:int=0, section=True, legend=True):
    if section:
        r.print_t('section', title=event, timespan=(log[0]['t'], log[-1]['t']))
    r.print_t('heatmap',
            heatmap=heatmap(filter_event(log, event, info_regex), bin),
            bin=bin, start_hour=6, end_hour=18,
            bin_size = bin, maxx=maxx, legend=legend
        )

def print_heatmap_daily(r:RenderHTML, daily, event:str, info_regex=None, bin:int=5, maxx:int=0, title=None):
    if not maxx:
        for log in daily:
            maxx = max(maxx, max(heatmap(filter_event(log, event, info_regex), bin)))
    r.print_t('section', title=title if title else event)
    r.print('<table>')
    for i, log in enumerate(daily):
        r.print('<tr><td>')
        r.print_t('section', date=log[0]['t'])
        r.print('</td><td>')
        legend = i==len(daily)-1
        print_heatmap(r, log, event, info_regex=info_regex, bin=bin, maxx=maxx, section=False, legend=legend)
        r.print('</td></tr>')
    r.print('</table>')

if args.format=='.html':
    r = RenderHTML(output=args.output)
    r.begin_print('Event heatmap')
    daily = split_daily(log)
    print_heatmap_daily(r, daily, 'SERVER_RECEIVE_LOG', title='Interactive is online (SERVER_RECEIVE_LOG)', bin=10, maxx=5)
    print_heatmap_daily(r, daily, 'PULL_LEVER', title='Lever pulled (PULL_LEVER)')
    print_heatmap_daily(r, daily, 'OPEN_OBJECT', title='Object clicked (OPEN_OBJECT)')
    print_heatmap_daily(r, daily, 'ON_PAGE', title='Editing or navigating story UI (ON_PAGE)')
    print_heatmap_daily(r, daily, 'POST_STORY', title='Story posted (POST_STORY)')
    r.end_print()
else:
    print('Unknown output format: '+args.format, file=sys.stderr)
