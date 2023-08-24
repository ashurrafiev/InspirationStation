import re
from datetime import datetime
from collections import Counter

def parse_log(path:str) -> list:
    def parse_line(line:str) -> dict:
        vs = line.split('\t', 2)
        return {
            't': datetime.strptime(vs[0], "%Y-%m-%dT%H:%M:%S.%fZ"),
            'event': vs[1],
            'info': vs[2]
        }
    with open(path, 'r') as f:
        return [parse_line(line[:-1]) for line in f]

def filter_time(log:list, t_start=None, t_end=None) -> list:
    return list(filter(lambda e : (t_start is None or e['t']>=t_start) and (t_end is None or e['t']<t_end), log))

def split_daily(log:list) -> list:
    d = log[0]['t'].date()
    out = list()
    last = list()
    for e in log:
        ed = e['t'].date()
        if ed>d:
            out.append(last)
            d = ed
            last = list()
        last.append(e)
    out.append(last)
    return out

def find_sequences(log, open_event:str, close_event:str) -> list:
    out = list()
    last = list()
    on = False
    for e in log:
        if on:
            last.append(e)
        if e['event']==close_event:
            out.append(last)
            on = False
        if e['event']==open_event:
            last = list()
            on = True
    return out

def find_object_sequences(log:list) -> list:
    return find_sequences(log, 'OPEN_OBJECT', 'CLOSE_OBJECT')

def count_sequences_by_object(seqs) -> dict:
    return dict(Counter([seq[-1]['info'] for seq in seqs]))

def filter_event(log, event:str, info_regex=None) -> list:
    return list(filter(lambda e : (e['event']==event and (not info_regex or re.match(info_regex, e['info']))), log))

def heatmap(log, bin=10, start_hour=6, end_hour=18) -> list[int]:
    bins = (24-(end_hour-start_hour)) * 60 // bin
    out = [0] * bins
    for e in log:
        m = (e['t'].hour - start_hour) * 60 + e['t'].minute
        if m<0:
            continue
        i = m // bin
        if i>=bins:
            continue
        out[i] += 1
    return out
