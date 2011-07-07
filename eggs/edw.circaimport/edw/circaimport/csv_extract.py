import sys
import re

import csv

from pprint import pprint


def get_notifications_mapping(dbfile):
    notifications, not_matched = {}, {}
    user_re = re.compile('([a-zA-Z0-9_]+)@circa')

    dbreader = csv.reader(dbfile)
    for row in dbreader:
        user_match = user_re.match(row[0])

        values = []
        for val in row[1:]:
            val_items = val.split(':')
            assert len(val_items) == 2
            path, notif_type = tuple(val_items)
            values.append({'path': path, 'notif_type': int(notif_type)})

        if user_match is None:
            not_matched[row[0]] = values
        else:
            user = user_match.group(1)
            notifications[user] = values
    return notifications, not_matched


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python %s <path-to-file.csv>' % sys.argv[0]
        sys.exit(1)

    try:
        dbfile = open(sys.argv[1], 'rb')
        notifications, not_matched = get_notifications_mapping(dbfile)
        dbfile.close()
    except ValueError, e:
        print 'Usage: python %s <path-to-file.csv>' % sys.argv[0]
        sys.exit(1)

    pprint(not_matched)
    pprint(notifications)
