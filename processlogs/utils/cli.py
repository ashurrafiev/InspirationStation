import os
import argparse
from datetime import datetime, timedelta

from .parselog import *

def parse_datetime(s):
    if s[-1]=='Z':
        s = s[:-1]
    formats = [
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d'
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(s)

def parse_args(init_func=None, description=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input')
    parser.add_argument('--from', dest='t_start', type=parse_datetime, help='format: yyyy-mm-ddThh:mm[:ss[.ff]]')
    parser.add_argument('--until', dest='t_end', type=parse_datetime, help='format: yyyy-mm-ddThh:mm[:ss[.ff]]')
    parser.add_argument('-d', '--day', type=parse_datetime, help='overrides --from and --until, format: yyyy-mm-dd')
    parser.add_argument('-o', '--output')
    parser.add_argument('--html', dest='format', action='store_const', const='.html')
    parser.add_argument('--csv', dest='format', action='store_const', const='.csv')
    if init_func:
        init_func(parser)
    args = parser.parse_args()
    
    if not args.format:
        if args.output:
            _, args.format = os.path.splitext(args.output)
        else:
            args.format = '.csv'
    
    if args.day:
        args.t_start = args.day.replace(hour=0, minute=0, second=0, microsecond=0)
        args.t_end = args.day + timedelta(days=1)
    
    return args

def input_data(args) -> list:
    return filter_time(parse_log(args.input), args.t_start, args.t_end)