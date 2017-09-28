import sys
import re
from pprint import pprint


def get_acl_mapping(fd):
    acls, not_matched = {}, []
    row_re = re.compile('([a-zA-Z0-9_/]+)\s+(.*)')

    for row in fd:
        acl_match = row_re.match(row)
        if acl_match is None:
            not_matched.append(row)
        else:
            values = acl_match.group(2)
            values = [val.strip(')|(') for val in values.split(')|(')]
            values = [val.split(':')[0] for val in values]
            acls[acl_match.group(1)] = values

    return acls, not_matched


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python %s <path-to-file>' % sys.argv[0]
        sys.exit(1)

    try:
        fd = open(sys.argv[1], 'rb')
        acls, not_matched = get_acl_mapping(fd)
        fd.close()
    except ValueError:
        print 'Usage: python %s <path-to-file>' % sys.argv[0]
        sys.exit(1)

    pprint(not_matched)
    pprint(acls)
