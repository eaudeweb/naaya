import re
import os.path

from Globals import package_home
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.pagetemplate.pagetemplate import PageTemplate as Z3_PageTemplate
from zope.tales.tales import Context

from zope.i18n import interpolate
from naaya.core.zope2util import get_template_source

def manage_addEmailPageTemplate(self, id, text):
    ept = EmailPageTemplate(id, text)
    self._setObject(id, ept)
    return id

class EmailPageTemplate(SimpleItem, Z3_PageTemplate):
    meta_type = 'Naaya Email Page Template'
    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Edit', 'action':'manage_edit'},
    ) + SimpleItem.manage_options

    def __init__(self, id, text):
        self.id = id
        self._text = text

    def render_email(self, **kwargs):
        text = self.pt_render({'options': kwargs})

        def get_section(name):
            try:
                start = text.index('<%s>' % name) + len(name) + 2
                end = text.index('</%s>' % name, start)
            except ValueError:
                raise ValueError('Section "%s" not found in '
                    'email template output' % name)
            return text[start:end].strip()

        return {
            'subject': get_section('subject'),
            'body_text': get_section('body_text'),
        }

    def pt_getEngineContext(self, namespace):
        return CustomI18nContext(self.pt_getEngine(), namespace)

    _manage_edit_html = PageTemplateFile('zpt/emailpt_edit', globals())
    security.declareProtected(view_management_screens, 'manage_edit')
    def manage_edit(self, text=None, REQUEST=None):
        """ change the contents """

        if text is not None:
            self._text = text
            self._cook() # force re-compilation of template

        if REQUEST is not None:
            text = get_template_source(self)
            return self._manage_edit_html(REQUEST, text=text)

InitializeClass(EmailPageTemplate)

def EmailPageTemplateFile(filename, _prefix):
    if _prefix:
        if isinstance(_prefix, str):
            filename = os.path.join(_prefix, filename)
        else:
            filename = os.path.join(package_home(_prefix), filename)
    f = open(filename)
    content = f.read()
    f.close()
    id = os.path.basename(filename)
    return EmailPageTemplate(id, content)

class CustomI18nContext(Context):
    def __init__(self, engine, contexts):
        super(CustomI18nContext, self).__init__(engine, contexts)

    def translate(self, msgid, domain=None, mapping=None, default=None):
        options = self.contexts['options']

        lang = options.get('_lang', None)
        translate = options.get('_translate', None)
        if translate is None:
            translate = lambda msgid, lang: msgid

        msg = translate(msgid, lang=lang)
        return interpolate(msg, mapping)
