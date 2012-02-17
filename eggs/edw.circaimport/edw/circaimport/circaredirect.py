import operator
import os.path

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import PersistentMapping

from edw.circaimport import ui

DEFAULT_REDIRECT = {'alias': '', 'where': 'forum'} # in forum, no id translation
REDIRECTS = {}
SERVERS = ('forum', 'projects', 'archives')

for server in SERVERS:
    REDIRECTS.update({
    server:
        {
            'home': 'http://%s.eionet.europa.eu/$1' % server,
            'directory': 'http://%s.eionet.europa.eu/$1/member_search' % server,
            'library': 'http://%s.eionet.europa.eu/$1/library$2' % server
        }
    })

def CircaRedirectAddView(context, request):
    """ Add view (simpleView) for CircaRedirect """
    submit_add = request.get('submit_add', '')
    id = request.get('id', '')
    title = request.get('title', '')
    if submit_add:
        obj = CircaRedirect(id, title)
        parent = context.aq_parent
        parent._setObject(id, obj)
        request.RESPONSE.redirect(parent.absolute_url() + '/manage_main')
        return ''
    else:
        pt = PageTemplateFile('zpt/circaredirect/manage_add', globals())
        return pt.__of__(context)()

class CircaRedirect(SimpleItem, PropertyManager):
    """
    TODO: docstring about class

    """

    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        self.id = id
        self.title = title
        self.load_config_file()

    def load_config_file(self):
        """
        Reads redirects.txt from var/circa_import folder and if successful,
        updates redirection rules.

        """
        file_path = os.path.join(ui.upload_prefix, "redirects.txt")
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
        self.redirects = PersistentMapping(found)
        file.close()
        return found

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST):
        """
        Expected QUERYSTRING args:
        - `id`, required - id of old IG in CIRCA
        - `type`, required - type of redirect target - home, directory or
          library
        - `path`, optional - only used in "inside library" redirects

        """
        id = REQUEST.form.get('id', '')
        rtype = REQUEST.form.get('type', 'home')
        path = REQUEST.form.get('path', '')

        redirect = self.redirects.get(id, DEFAULT_REDIRECT)
        alias = id
        if redirect['alias']:
            alias = redirect['alias']
        new_path = REDIRECTS.get(redirect['where'], {}).get(rtype)
        new_path = new_path.replace('$1', alias).replace('$2', path)
        REQUEST.RESPONSE.redirect(new_path)
        REQUEST.RESPONSE.setStatus(301,
            reason="CIRCA Interest Groups migrated to eionet.europa.eu hosts")
        return None
