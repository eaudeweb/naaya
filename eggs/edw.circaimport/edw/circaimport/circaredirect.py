import time
import os
from copy import deepcopy

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from edw.circaimport import ui

redirect_records = {'last-load': None, 'data': {}}
DEFAULT_REDIRECT = {'alias': '', 'where': 'forum'} # in forum, no id translation
SERVERS = ('forum', 'projects', 'archives')
REDIRECTS = {} # filled here
for server in SERVERS:
    REDIRECTS.update({
    server:
        {
            'home': 'http://%s.eionet.europa.eu/$1' % server,
            'directory': 'http://%s.eionet.europa.eu/$1/member_search' % server,
            'library': 'http://%s.eionet.europa.eu/$1/library$2' % server
        }
    })

def load_config_file():
    """
    Reads redirects.txt from var/circa_import folder and if successful,
    updates redirection rules.

    """
    if not ui.upload_prefix:
        return None
    file_path = os.path.join(ui.upload_prefix, "redirects.txt")
    modification_time = os.stat(file_path).st_mtime
    if modification_time == redirect_records['last-load']:
        return None
    file = open(file_path, "r")
    found = {}
    for (i, line) in enumerate(file):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        tokens = line.split()
        if len(tokens) == 1:
            tokens.extend(['forum', ''])
        elif len(tokens) == 2:
            tokens.append('')
        elif len(tokens) > 3:
            file.close()
            raise ValueError("Found more than 3 tokens on line #%d" % (i+1))
        found[tokens[0]] = {'where': tokens[1], 'alias': tokens[2]}
    redirect_records['data'] = deepcopy(found)
    redirect_records['last-load'] = modification_time
    file.close()

def circa_redirect(context, request):
    """
    Expected QUERYSTRING args:
    - `id`, required - id of old IG in CIRCA
    - `type`, required - type of redirect target - home, directory or
      library
    - `path`, optional - only used in "inside library" redirects

    """
    load_config_file()
    id = request.form.get('id', '')
    rtype = request.form.get('type', 'home')
    path = request.form.get('path', '')

    redirect = redirect_records['data'].get(id, DEFAULT_REDIRECT)
    alias = id
    if redirect['alias']:
        alias = redirect['alias']
    new_path = REDIRECTS.get(redirect['where'], {}).get(rtype)
    new_path = new_path.replace('$1', alias).replace('$2', path)
    request.RESPONSE.redirect(new_path)
    request.RESPONSE.setStatus(301,
        reason="CIRCA Interest Groups migrated to eionet.europa.eu hosts")
    return None

def circa_redirect_inspector(context, request):
    """ Debugger when connecting to machine is not desirable """
    load_config_file()
    pt = PageTemplateFile("zpt/circaredirect/inspector.zpt", globals())
    return pt.__of__(context)(redirects=redirect_records['data'],
                    last_modification=time.ctime(redirect_records['last-load']))
