# usage:
# python3 report_engagement.py logs/filename.txt > reports/output.html

import sys
from parselog import *
from render import Render

log = parse_log(sys.argv[1])

def count_displayed(log:list) -> dict:
    d = list()
    for e in filter_event(log, 'DISPLAY_OBJECTS'):
        d += e['info'].split(',')
    return dict(Counter(d))

c_disp = count_displayed(log)
ids = sorted(c_disp.keys())

obj = find_object_sequences(log)
c_obj = count_sequences_by_object(obj)
c_started = count_sequences_by_object(filter(lambda seq : filter_event(seq, 'ON_PAGE'), obj))
c_done = count_sequences_by_object(filter(lambda seq : filter_event(seq, 'DONE_CHECK', r'^ok$'), obj))
c_sent = count_sequences_by_object(filter(lambda seq : filter_event(seq, 'STORY_UID'), obj))

table = [[ i, c_disp.get(i, 0), c_obj.get(i, 0), c_started.get(i, 0), c_done.get(i, 0), c_sent.get(i, 0) ] for i in ids]
totals = [ 'Total', sum(c_disp.values()), sum(c_obj.values()), sum(c_started.values()), sum(c_done.values()), sum(c_sent.values()) ]

r = Render()
r.begin_print('Test Report')
r.print_t('table',
        title='User engagement by object',
        timespan=(log[0]['t'], log[-1]['t']),
        cols=['Object', 'Shown', 'Clicked', 'Started story', 'Finished story', 'Posted story'],
        table=table,
        totals=totals
    )
r.end_print()
