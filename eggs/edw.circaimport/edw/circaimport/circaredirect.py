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
            'home': 'http://%s.eionet.europa.eu/%%(alias)s' % server,
            'directory': 'http://%s.eionet.europa.eu/%%(alias)s/member_search' % server,
            'library': 'http://%s.eionet.europa.eu/%%(alias)s/library%%(path)s' % server
        }
    })

def get_configuration():
    """
    Reads redirects.txt from var/circa_import folder and if successful,
    updates redirection rules.

    Returns known redirection rules.
    Raises ValueError if file not properly parsed.

    """
    if not ui.upload_prefix:
        return None
    file_path = os.path.join(ui.upload_prefix, "redirects.txt")
    modification_time = os.stat(file_path).st_mtime
    if modification_time == redirect_records['last-load']:
        return redirect_records['data']

    found = {}
    config_file = open(file_path, "r")
    try:
        for (i, line) in enumerate(config_file):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            tokens = line.split()
            if len(tokens) == 1:
                tokens.extend(['forum', ''])
            elif len(tokens) == 2:
                tokens.append('')
            elif len(tokens) > 3:
                raise ValueError("Found more than 3 tokens on line #%d" % (i+1))
            found[tokens[0]] = {'where': tokens[1], 'alias': tokens[2]}
        redirect_records['data'] = deepcopy(found)
        redirect_records['last-load'] = modification_time
        return redirect_records['data']
    finally:
        config_file.close()

def circa_redirect(context, request):
    """
    Expected QUERYSTRING args:
    - `id`, required - id of old IG in CIRCA
    - `type`, required - type of redirect target - home, directory or
      library
    - `path`, optional - only used in "inside library" redirects

    """
    id = request.form.get('id', '')
    rtype = request.form.get('type', 'home')
    path = request.form.get('path', '')

    redirects_config = get_configuration()
    redirect = redirects_config.get(id, DEFAULT_REDIRECT)
    alias = id
    if redirect['alias']:
        alias = redirect['alias']
    new_path = REDIRECTS.get(redirect['where'], {}).get(rtype)
    new_path = new_path % {'alias': alias, 'path': path}
    request.RESPONSE.redirect(new_path)
    request.RESPONSE.setStatus(301,
        reason="CIRCA Interest Groups migrated to eionet.europa.eu hosts")
    return None

def circa_redirect_inspector(context, request):
    """ Debugger when connecting to machine is not desirable """
    redirects_config = get_configuration()
    pt = PageTemplateFile("zpt/circaredirect/inspector.zpt", globals())
    return pt.__of__(context)(redirects=redirects_config,
                    last_modification=time.ctime(redirect_records['last-load']))
