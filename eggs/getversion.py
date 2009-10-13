import os
def get_svn_version():
    if not os.path.isdir('.svn'):
        return '1.0dev-r0'
    svn_info = os.popen('svn info').readlines()
    for line in svn_info:
        if 'Revision' in line:
            revision = line.split(':')[1].strip()
            return '1.0dev-r%s' % revision
    return '1.0dev-rUNKNOWN'

def get_version():
    return get_svn_version()

