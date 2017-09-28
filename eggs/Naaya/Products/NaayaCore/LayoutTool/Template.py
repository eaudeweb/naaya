from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.NaayaCore.constants import *
from Products.NaayaCore.FormsTool.interfaces import ITemplate
from naaya.core.zope2util import get_template_source

from interfaces import INyTemplate

manage_addTemplateForm = PageTemplateFile('zpt/template_add', globals())
def manage_addTemplate(self, id='', title='', file='', content_type='text/html', REQUEST=None):
    """ """
    file_content = ''
    if file != '':
        if file.filename:
            headers = getattr(file, 'headers', None)
            content_type = content_type or headers.get('content-type')
            file_content = file.read()
            id = id or file.filename.split('.')[0]
    ob = Template(id, title, file_content, content_type)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class Template(ZopePageTemplate):
    """ """
    implements(INyTemplate, ITemplate)

    meta_type = METATYPE_TEMPLATE
    icon = 'misc_/NaayaCore/Template.gif'

    manage_options = (
        ZopePageTemplate.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, text, content_type):
        """ """
        ZopePageTemplate.__dict__['__init__'](self, id, text, content_type)
        self.title = title

    def __call__(self, *args, **kwargs):
        """ """
        context={'args': args}
        if kwargs:
            context['options'] = kwargs
        try:
            response = self.REQUEST.RESPONSE
            if not response.headers.has_key('content-type'):
                response.setHeader('content-type', self.content_type)
        except AttributeError:
            pass
        return self.pt_render(extra_context=context)

    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                'alt': 'Error', 'title': 'This template has an error'},)
        return icons

    @property
    def source(self):
        return get_template_source(self)

InitializeClass(Template)
