"""
This tool is used as a way to customize Zope Page Templates directly in ZMI.

The templates are registered as utilities. Templates can be registered using the
global registry, bundles or local site managers. The later only happens when
they are modified using the ZMI interface.

The resolution of templates is hierarchical and the lookup is usually performed in this order::

    :term:`Local site manager` -> :term:`Bundle` (specific site bundle) -> :term:`Bundle` (more general) -> :term:`Global site manager`

If a template is customized using the ZMI interface then it should be in the
:term:`Local site manager` otherwise look in bundles and at the end in
the :term:`Global site manager`.

This is useful when some templates must be customized in different Naaya Sites.
It also provides a way to keep track of the changes made and their differences
using diff tools.

"""
import os
import logging
from App.ImageFile import ImageFile
from Globals import InitializeClass
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.deprecation import deprecate
from zope.component import ComponentLookupError
from zope.component import getGlobalSiteManager

from Products.NaayaCore.constants import (METATYPE_FORMSTOOL, METATYPE_TEMPLATE,
ID_FORMSTOOL, TITLE_FORMSTOOL, PERMISSION_ADD_NAAYACORE_TOOL, )
from Products.NaayaCore.LayoutTool.Template import (
    manage_addTemplateForm, manage_addTemplate, Template)

from Products.NaayaCore.managers.utils import html_diff

from interfaces import ITemplate, IFilesystemTemplateWriter
from NaayaTemplate import NaayaPageTemplateFile
from naaya.core import fsbundles
from naaya.core.zope2util import get_template_source


log = logging.getLogger(__name__)


def manage_addFormsTool(self, REQUEST=None):
    """ Forms tool constructor """
    ob = FormsTool(ID_FORMSTOOL, TITLE_FORMSTOOL)
    self._setObject(ID_FORMSTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class FormsTool(Folder):
    """Class that implements a container for forms."""

    meta_type = METATYPE_FORMSTOOL
    icon = 'misc_/NaayaCore/FormsTool.gif'

    manage_options = (
        {'label':'All forms', 'action':'manage_overview'},
        Folder.manage_options[0],
        Folder.manage_options[1],
        Folder.manage_options[4],
    ) + Folder.manage_options[7:]

    meta_types = ({
        'name': METATYPE_TEMPLATE,
        'action': 'manage_addTemplateForm',
        'permission': PERMISSION_ADD_NAAYACORE_TOOL
    },)
    all_meta_types = meta_types

    manage_addTemplateForm = manage_addTemplateForm
    manage_addTemplate = manage_addTemplate

    manage_overview = PageTemplateFile('zpt/manage_overview', globals())
    manage_customize = PageTemplateFile('zpt/manage_customize', globals())
    _diff = PageTemplateFile('zpt/diff', globals())

    tool_js = ImageFile('www/tool.js', globals())

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def get_template(self, name):
        """ Get template from the local site manager """
        sm = self.getSite().getSiteManager()
        return sm.getUtility(ITemplate, name)

    def bundle_template(self, name):
        """
        Get template from site's bundle.
        This is used to make a diff between the customized template from the
        local site manager and the bundle version
        """
        sm = self.getSite().get_bundle()
        return sm.getUtility(ITemplate, name)

    security.declareProtected(view_management_screens, 'get_all_templates')
    def get_all_templates(self):
        """ Get all templates """
        sm = self.getSite().getSiteManager()
        # getUtilitiesFor returns a tuple of (name, utility).
        return sorted(sm.getUtilitiesFor(ITemplate))

    def registered_templates(self):
        return [str(name) for name, tpl in self.get_all_templates()]

    def template_content(self, name):
        """ Get template content """
        template = self.get_template(name)
        return get_template_source(template)

    def getForm(self, name):
        """ Fetches a Naaya form. """
        try:
            tmpl = self.get_template(name)
        except ComponentLookupError:
            raise KeyError("No such template: %r" % name)
        else:
            return tmpl.__of__(self)

    def __getitem__(self, name):
        """ Same as above """
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

    security.declareProtected(view_management_screens, 'show_diff')
    def show_diff(self, REQUEST):
        """ show the differences between the default and customized form """
        name = REQUEST.get('name', '')
        bundle_template = self.bundle_template(name)
        bundle_content = get_template_source(bundle_template)

        customized_content = self.template_content(name)

        diff = html_diff(bundle_content, customized_content)
        return self._diff(diff=diff)

    def customized_templates(self):
        """Get customized templates"""
        return [name for name, template in self.get_all_templates()
                if not isinstance(template, NaayaPageTemplateFile)]

    def bundle_templates(self):
        sm = self.getSite().get_bundle()
        return set(name for name, tmpl in sm.getUtilitiesFor(ITemplate))

    security.declareProtected(view_management_screens, 'manage_customizeForm')
    def manage_customizeForm(self, name, REQUEST=None):
        """ Copy the form from disk to zodb """
        body = self.template_content(name)
        ob = Template(id=name, title=name, text=body,
                content_type='text/html')
        ob._naaya_original_text = body
        self._setObject(name, ob)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' %
                                             (self.absolute_url(), name))


    def can_write_to_bundle(self):
        """ Check if we can find (or create) any bundle to write templates. """
        site = self.getSite()
        if fsbundles.get_writable_bundle(site) is not None:
            return True
        elif fsbundles.get_filesystem_bundle_factory(site) is not None:
            return True
        else:
            return False


    security.declareProtected(view_management_screens, 'move_to_bundle')
    def move_to_bundle(self, REQUEST=None):
        """ Move templates to a writable bundle. """

        site = self.getSite()
        user = site.getAuthenticationTool().get_current_userid()

        bundle = fsbundles.get_writable_bundle(site)

        if bundle is None:
            factory = fsbundles.get_filesystem_bundle_factory(site)
            assert factory is not None, "No writable bundle found!"
            bundle = factory()

            if REQUEST is not None:
                msg = ("IMPORTANT: new bundle %r created. If multiple Zope "
                       "instances are sharing the same ZEO database, make "
                       "sure they all load the new bundle." % bundle)
                self.setSessionInfo([msg])

        bundle_name = bundle.__name__
        gsm = getGlobalSiteManager()
        writer = gsm.queryUtility(IFilesystemTemplateWriter, name=bundle_name)

        template_names = []
        for template in self.objectValues():
            content = get_template_source(template)
            name = template.getId()

            writer.write_zpt(name, content)
            self._delObject(template.getId())

            log.info("Template %r moved to bundle %r by %r",
                     name, bundle_name, user)
            template_names.append(name)

        # TODO reload the bundle in all zope instances

        # TODO in case of failure, print what has been written to disk

        if REQUEST is not None:
            self.setSessionInfo(["Moved templates bundle %r: %r" %
                                (bundle_name, template_names)])
            return REQUEST.RESPONSE.redirect('%s/manage_overview' %
                                             self.absolute_url())


InitializeClass(FormsTool)
