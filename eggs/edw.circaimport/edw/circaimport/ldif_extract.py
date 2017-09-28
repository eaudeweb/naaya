import sys
import tarfile
from ldif import LDIFParser
from pprint import pprint
import os

from App.config import getConfiguration

CONFIG = getConfiguration()
CONFIG.environment.update(os.environ)
CIRCA_CIRCLE_NAME = getattr(CONFIG, 'environment', {}).get('CIRCA_CIRCLE_NAME', 'eionet-circle')

class LDIFClassesParser(LDIFParser):
    """
    Parses entries that look like this::

    dn: cn=4, ...
    description: Class=4 ...
    cn: 4
    cn: 4-...
    classname: DE:Sekretaer
    classname: FR:Secretaire
    classname: EN:Secretary
    overwrites: 000 000 000 000 000 000
    grouprole: 000 000 007 FFF 000 000
    objectclass: top
    objectclass: groupOfUniqueNames
    objectclass: igclass

    """
    def __init__(self, descriptor):
        self.classes = {}
        LDIFParser.__init__(self, descriptor)

    def handle(self, dn, entry):
        assert 'objectclass' in entry
        if 'igclass' not in entry['objectclass']:
            return

        assert 'classname' in entry
        assert 'cn' in entry
        assert 'grouprole' in entry

        cn = int(entry['cn'][0])
        classnames = [c for c in entry['classname'] if c.startswith('EN:')]
        assert len(classnames) == 1
        classname = classnames[0][3:]

        self.classes[cn] = classname


class LDIFUsersParser(LDIFParser):
    """
    Parses entries that look like this::

    dn: iguid=userid@circa, ...
    userclass: 0
    overwrites: 000 000 000 000 000 000
    iguid: userid@circa
    grouprole: FFF FFF FFF FFF FFF FFF
    objectclass: top
    objectclass: iguser
    """
    def __init__(self, descriptor):
        self.users = {}
        LDIFParser.__init__(self, descriptor)

    def handle(self, dn, entry):
        assert 'objectclass' in entry
        if 'iguser' not in entry['objectclass']:
            return
        if 'userclass' not in entry:
            return
        if 'grouprole' not in entry:
            return

        assert len(entry['userclass']) == 1
        assert len(entry['iguid']) == 1
        assert entry['iguid'][0].endswith('@circa')

        uid = entry['iguid'][0][:-6]
        assert dn.startswith('iguid=%s@circa' % uid)

        userclass = int(entry['userclass'][0])

        self.users[uid] = userclass


class LDIFRolesParser(LDIFParser):
    """
    Parses entries that look like this::

    dn: igrid=staff, ...
    igrid: staff
    roleclass: 1
    overwrites: 000 000 000 000 000 000
    grouprole: 001 001 001 001 001 001
    objectclass: top
    objectclass: igrole
    """
    def __init__(self, descriptor):
        self.roles = {}
        LDIFParser.__init__(self, descriptor)

    def handle(self, dn, entry):
        assert 'objectclass' in entry
        if 'igrole' not in entry['objectclass']:
            return
        if 'roleclass' not in entry:
            return
        if 'grouprole' not in entry:
            return

        rid = entry['igrid'][0]
        roleclass = int(entry['roleclass'][0])
        self.roles[rid] = roleclass


class LDIFOpener(object):
    def __init__(self, path):
        head, tail = os.path.split(path)
        name, ext = os.path.splitext(tail)
        if ext == '.tgz':
            fd = tarfile.open(path, 'r')
            fd_ldif = fd.extractfile('%s/ldap/%s.%s.ircnode.ldif'
                             % (name, CIRCA_CIRCLE_NAME, name))
            self.fd, self.fd_ldif = fd, fd_ldif
        elif ext == '.ldif':
            self.fd_ldif = open(path, 'r')
        else:
            raise ValueError('Path is not to a .tgz or .ldif file')

    def close(self):
        self.fd_ldif.close()
        if hasattr(self, 'fd'):
            self.fd.close()


def ldif_extract(path):
    opener = LDIFOpener(path)

    classes_parser = LDIFClassesParser(opener.fd_ldif)
    classes_parser.parse()

    opener.fd_ldif.seek(0)

    users_parser = LDIFUsersParser(opener.fd_ldif)
    users_parser.parse()

    opener.fd_ldif.seek(0)

    roles_parser = LDIFRolesParser(opener.fd_ldif)
    roles_parser.parse()

    opener.close()

    return classes_parser.classes, users_parser.users, roles_parser.roles


def get_role_from_ldif_classname(classname):
    LDIF_CLASS_2_ROLE = {
            'Access': 'Viewer',
            'Anonymous': 'Anonymous',
            'Author': 'Contributor',
            'Contributor': 'Viewer',
            'Leader': 'Administrator',
            'Registered': 'Authenticated',
            'Secretary': 'Viewer'
            }
    DEFAULT_ROLE = 'Viewer'

    if classname in LDIF_CLASS_2_ROLE:
        return LDIF_CLASS_2_ROLE[classname]
    return DEFAULT_ROLE


def get_user_and_group_mapping(path):
    ldif_classes, ldif_users, ldif_roles = ldif_extract(path)

    ldif_class_2_role = dict((_class, get_role_from_ldif_classname(classname))
                                for _class, classname in ldif_classes.items())

    user_2_role = dict((user, ldif_class_2_role[userclass])
                        for user, userclass in ldif_users.items())

    group_2_role = dict((group, ldif_class_2_role[groupclass])
                        for group, groupclass in ldif_roles.items())

    return user_2_role, group_2_role


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python %s <path-to-file.tgz>' % sys.argv[0]
        sys.exit(1)

    try:
        user_2_role, group_2_role = get_user_and_group_mapping(sys.argv[1])
    except ValueError:
        print 'Usage: python %s <path-to-file.tgz>' % sys.argv[0]
        sys.exit(1)

    pprint(user_2_role)
    pprint(group_2_role)
