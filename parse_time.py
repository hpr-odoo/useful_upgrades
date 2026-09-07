#!/usr/bin/env python3

import datetime as dt
import re
import sys

if len(sys.argv) < 2:
    print("usage: {} <log_file> [<from_time>]".format(__file__))
    exit(1)
from_time = None
if len(sys.argv) == 3:
    from_time = dt.datetime.fromisoformat(sys.argv[2])

date_re = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}\:\d{2}).+")
data = []
last_t = None
last_line = None
delta = dt.timedelta(minutes=1)
fname = sys.argv[1]
with open(fname, "rt") as f:
    for line in f:
        # --------------------------------------------------------------
        # If you want the files name instead of every line of execuation
        # uncomment below line
        # --------------------------------------------------------------
        # if not(word in f for word in ['pre-', 'post-', 'end-', 'init-', 'loading', 'Mocking menu']):
        #     continue
        m = date_re.match(line)
        if not m:
            continue
        t = dt.datetime.fromisoformat(m.group(1))
        if from_time and t < from_time:
            continue
        if last_t and t - last_t > delta:
            data.append((t - last_t, last_line))
        last_t = t
        last_line = line
data.sort()
data.reverse()
for d in data[:10]:
    print(d)
