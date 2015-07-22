# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

"""
This module contains the class that implements a container
for Naaya CMF common forms (page templates).

This is a core tool of the Naaya CMF.
Every portal B{must} have an object of this type inside.
"""

#Python imports
from os.path import join

#Zope imports
from Globals import InitializeClass
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.LayoutTool.Template import manage_addTemplateForm, manage_addTemplate, Template

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
        {'label':'All forms', 'action':'manage_customize'},
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
        """
        Creates default stuff.
        I{(Nothing for the moment.)}
        """
        pass

    def listDefaultForms(self):
        """
        generator that yields all default forms
        """
        # get forms from skel folders
        for skel_handler in reversed(self.get_all_skel_handlers()):
            if skel_handler.root.forms is None:
                continue

            skel_path = skel_handler.skel_path
            for form in skel_handler.root.forms.forms:
                path = join(skel_path, 'forms', '%s.zpt' % form.id)
                yield {'id': form.id, 'title': form.title, 'path': path}

        # get forms from pluggable items
        pluggable_content = self.get_pluggable_content()

        for meta_type, pluggable_item in pluggable_content.iteritems():
            for form_id in pluggable_item['forms']:
                module_name = pluggable_item['module']
                title = '%s %s' % (module_name, form_id)
                path = join(pluggable_item['package_path'], 'zpt', '%s.zpt' % form_id)
                yield {'id': form_id, 'title': title, 'path': path}

        # forms of type NaayaPageTemplateFile
        for form_id, tmpl in naaya_templates.iteritems():
            yield {'id': form_id, 'title': form_id, 'form_ob': tmpl}

    def getDefaultForm(self, form_id):
        for form in self.listDefaultForms():
            if form['id'] == form_id:
                if 'form_ob' in form:
                    return form['form_ob']._text
                else:
                    return self.futRead(form['path'], 'r')
        else:
            raise KeyError('Not found form named "%s"' % form_id)

    def getForm(self, form_id):
        """
        Fetches a Naaya form

        First looks in the portal_forms folder (in case the form has been
        customized). If not, then it looks for default templates in packages.
        """
        if form_id in self.objectIds():
            return self._getOb(form_id)
        else:
            for form in self.listDefaultForms():
                if form['id'] == form_id:
                    if 'form_ob' in form:
                        return form['form_ob'].__of__(self)

                    body=self.futRead(form['path'], 'r')
                    t = Template(id=form['id'],
                                 title=form['title'],
                                 text=body,
                                 content_type='')
                    return t.__of__(self)
            raise KeyError('Not found form named "%s"' % form_id)

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
        return form(p_context)

    security.declareProtected(view_management_screens, 'manage_customizeForm')
    def manage_customizeForm(self, form_id, REQUEST=None):
        """ Copy the form from disk to zodb """
        for form in self.listDefaultForms():
            if form['id'] == form_id:
                if 'form_ob' in form:
                    body = form['form_ob']._text
                else:
                    body = self.futRead(form['path'], 'r')
                break
        else:
            raise KeyError('Not found form named "%s"' % form_id)

        ob = Template(id=form['id'],
                      title=form['title'],
                      text=body,
                      content_type='text/html')
        ob._naaya_original_text = body
        self._setObject(form['id'], ob)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' %
                (self.absolute_url(), form['id']))

    manage_customize = PageTemplateFile('zpt/customize', globals())

InitializeClass(FormsTool)

naaya_templates = {}
def register_naaya_template(tmpl, form_id):
    naaya_templates[form_id] = tmpl
