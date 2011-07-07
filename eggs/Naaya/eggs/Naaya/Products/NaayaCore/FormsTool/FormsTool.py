"""
This tool is used as a way to customize PageTemplates directly in ZMI. The
templates are usually registered from skel or as NaayaPageTemplates.
This is useful when some templates must be customized in different Naaya Sites.

It also provides a way to keep track of the changes made and their differences
using diff tools.

"""

from os.path import join

from Globals import InitializeClass
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *
from Products.NaayaCore.LayoutTool.Template import (
    manage_addTemplateForm, manage_addTemplate, Template)
from Products.NaayaCore.managers.utils import html_diff
import naaya.content.base.discover

def get_template_file(template_path, name, _memo={}):
    if template_path in _memo:
        template = _memo[template_path]
    else:
        template = PageTemplateFile(template_path, __name__=name)
        _memo[template_path] = template
    return template

naaya_templates = {}
def register_naaya_template(tmpl, name):
    naaya_templates[name] = tmpl

def get_templates_from_skel(skel_handler):
    if skel_handler.root.forms is None:
        return

    skel_path = skel_handler.skel_path
    for form in skel_handler.root.forms.forms:
        path = join(skel_path, 'forms', '%s.zpt' % form.id)
        yield get_template_file(path, name=form.id)

def get_templates_from_pluggable_content():
    pluggable_content = naaya.content.base.discover.get_pluggable_content()

    for meta_type, pluggable_item in pluggable_content.iteritems():
        for name in pluggable_item.get('forms', []):
            module_name = pluggable_item['module']
            path = join(pluggable_item['package_path'], 'zpt', '%s.zpt' % name)
            yield get_template_file(path, name=name)

def get_templates_from_naaya_code():
    # forms of type NaayaPageTemplateFile
    return naaya_templates.itervalues()


def manage_addFormsTool(self, REQUEST=None):
    """
    Class that implements the tool.
    """
    ob = FormsTool(ID_FORMSTOOL, TITLE_FORMSTOOL)
    self._setObject(ID_FORMSTOOL, ob)
    self._getOb(ID_FORMSTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class FormsTool(Folder):
    """
    Class that implements a container for forms.
    """

    meta_type = METATYPE_FORMSTOOL
    icon = 'misc_/NaayaCore/FormsTool.gif'

    manage_options = (
        {'label':'All forms', 'action':'manage_overview'},
        Folder.manage_options[0],
        Folder.manage_options[1],
        Folder.manage_options[4],
    ) + Folder.manage_options[7:]

    meta_types = (
        {'name': METATYPE_TEMPLATE, 'action': 'manage_addTemplateForm', 'permission': PERMISSION_ADD_NAAYACORE_TOOL},
    )
    all_meta_types = meta_types

    manage_addTemplateForm = manage_addTemplateForm
    manage_addTemplate = manage_addTemplate

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """

    security.declareProtected(view_management_screens, 'listDefaultForms')
    def listDefaultForms(self):
        """
        generator that yields all default forms
        """
        # get forms from skel folders
        for skel_handler in reversed(self.get_all_skel_handlers()):
            for template in get_templates_from_skel(skel_handler):
                yield template

        for template in get_templates_from_pluggable_content():
            yield template

        for template in get_templates_from_naaya_code():
            yield template

    security.declareProtected(view_management_screens, 'registered_templates')
    def registered_templates(self):
        return sorted(set(tmpl.__name__ for tmpl in self.listDefaultForms()))

    def getDefaultForm(self, name):
        for template in self.listDefaultForms():
            if template.__name__ == name:
                return template._text
        else:
            raise KeyError('Could not find template %r' % name)

    def _default_form(self, name):
        """ get the non-customized form """
        for template in self.listDefaultForms():
            if template.__name__ == name:
                break
        else:
            raise KeyError('Could not find template %r' % name)

        return template.__of__(self)

    def getForm(self, name):
        """
        Fetches a Naaya form

        First looks in the portal_forms folder (in case the form has been
        customized). If not, then it looks for default templates in packages.
        """
        if name in self.objectIds():
            return self._getOb(name)
        else:
            return self._default_form(name)

    def __getitem__(self, name):
        """
        Makes it possible to access portal forms by key
        and therefore by `path:` traversal in zpt.

        """
        return self.getForm(name)

    def getContent(self, p_context={}, p_page=None):
        """
        Renders the given form and return the result.
        @param p_context: extra parameters for the ZPT
        @type p_context: dictionary
        @param p_page: the id of the ZPT
        @type p_page: string
        """

        p_context['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
        form = self.getForm(p_page)
        return form.pt_render(extra_context=p_context)

    _diff = PageTemplateFile('zpt/diff', globals())
    security.declareProtected(view_management_screens, 'show_diff')
    def show_diff(self, REQUEST):
        """ show the differences between the default and customized form """
        name = REQUEST.get('name', '')
        form_customized = self._getOb(name)
        form_default = self._default_form(name)
        diff = html_diff(form_default._text, form_customized._text)
        return self._diff(diff=diff)

    security.declareProtected(view_management_screens, 'manage_customizeForm')
    def manage_customizeForm(self, name, REQUEST=None):
        """ Copy the form from disk to zodb """
        for template in self.listDefaultForms():
            if template.__name__ == name:
                body = template._text
                break
        else:
            raise KeyError('Could not find template %r' % name)

        ob = Template(id=name, title=name, text=body, content_type='text/html')
        ob._naaya_original_text = body
        self._setObject(name, ob)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' %
                                             (self.absolute_url(), name))

    manage_overview = PageTemplateFile('zpt/manage_overview', globals())
    manage_customize = PageTemplateFile('zpt/manage_customize', globals())

InitializeClass(FormsTool)
