import sys
import re

import csv

from pprint import pprint


def get_notifications_mapping(filepath):
    notifications, not_matched = {}, {}
    user_re = re.compile('([a-zA-Z0-9_]+)@circa')

    dbfile = open(filepath, 'rb')
    dbreader = csv.reader(dbfile)
    for row in dbreader:
        user_match = user_re.match(row[0])
        values = row[1:]

        if user_match is None:
            not_matched[row[0]] = values
        else:
            user = user_match.group(1)
            notifications[user] = values
    dbfile.close()
    return notifications, not_matched


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python %s <path-to-file.csv>' % sys.argv[0]
        sys.exit(1)

    try:
        notifications, not_matched = get_notifications_mapping(sys.argv[1])
    except ValueError:
        print 'Usage: python %s <path-to-file.csv>' % sys.argv[0]
        sys.exit(1)

    pprint(not_matched)
    pprint(notifications)
