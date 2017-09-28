#!/usr/bin/env python
import os
import json

NAME = 'site.log'


def rewrite_logs(path):
    to_process = []
    for name in os.listdir(path):
        if name.startswith(NAME):
            to_process.append(name)

    entries = {}

    for name in to_process:
        fname = os.path.join(path, name)
        with open(fname) as f:
            counter = 0
            for line in f:
                counter += 1
                try:
                    data = json.loads(line)
                except:
                    print "Line %s could not be parsed in file %s" % (
                        counter, fname)
                    continue
                date = data['asctime']
                ident = date[:5]  # date looks like: "12-09-17 17:02:49,451019"
                if not ident in entries:
                    entries[ident] = []

                entries[ident].append(line)

    for ident in entries.keys():
        flog = os.path.join(path, "splitlog-" + ident + '.log')
        with open(flog, 'w') as log:
            log.writelines(entries[ident])


if __name__ == "__main__":
    for name in os.listdir('.'):
        if os.path.isdir(name):
            rewrite_logs(name)
