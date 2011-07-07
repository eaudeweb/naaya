import sys
import re

from pprint import pprint

def get_notifications_mapping(dbprintedfd):
    notifications, not_matched = {}, {}
    row_re = re.compile('([a-zA-Z0-9_@]+)\s+(.*)')
    user_re = re.compile('([a-zA-Z0-9_]+)@circa')

    for row in dbprintedfd:
        row_match = row_re.match(row)
        if row_match is None:
            if None not in not_matched:
                not_matched[None] = []
            not_matched[None].append(row)
            continue

        raw_values = row_match.group(2)
        raw_values = [val.strip(')|(') for val in raw_values.split(')|(')]
        values = []
        for val in raw_values:
            val_items = val.split(':')
            assert len(val_items) == 2
            path, notif_type = tuple(val_items)
            values.append({'path': path, 'notif_type': int(notif_type)})

        user_match = user_re.match(row_match.group(1))
        if user_match is None:
            notifications[row_match.group(1)] = values
        else:
            notifications[user_match.group(1)] = values

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
