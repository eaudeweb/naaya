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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Andrei Laza, Eau de Web


#Python imports
import copy

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript
from Products.naayaUpdater.utils import *

class UpdateNaayaForms(UpdateScript):
    """ Update Naaya forms script  """
    id = 'overwritte_forms_html'
    title = 'Update Naaya forms'
    authors = ['Cornel Nitu']

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'diff_forms_html')
    diff_forms_html = PageTemplateFile('zpt/diff_forms', globals())

    security.declareProtected(view_management_screens, 'absolute_url')
    def absolute_url(self):
        return self.aq_parent.get_update_script_url(self.update_id)

    security.declareProtected(view_management_screens, 'getReportModifiedForms')
    def getReportModifiedForms(self, ppath, REQUEST=None):
        """ overwritte Naaya portal forms """
        if REQUEST.has_key('show_report'):
            portal = self.getPortal(ppath)
            out_modified = []
            modified, unmodified, list_diff = self.get_modified_forms(portal)
            #check for modified
            buf = copy.copy(modified)
            for m in buf:
                zmi = self.get_fs_template(m.id, portal)
                if create_signature(self.get_template_content(m)) == create_signature(zmi):
                    modified.remove(m)
            #check for unmodified
            buf = copy.copy(unmodified)
            for m in buf:
                zmi = self.get_fs_template(m.id, portal)
                if create_signature(self.get_template_content(m)) == create_signature(zmi):
                    unmodified.remove(m)
            out_modified.extend(modified)
            return out_modified, len(unmodified)

    security.declareProtected(view_management_screens, 'testFTCreationDate')
    def testFTCreationDate(self, portal):
        """
            test PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        return hasattr(forms_tool, 'creation_date')

    security.declareProtected(view_management_screens, 'setFTDateFormsPage')
    def setFTDateFormsPage(self, ppath, REQUEST=None):
        """
            Set creation date
        """
        portal = self.getPortal(ppath)
        self.setFTCreationDate(portal)
        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?ppath=%s&show_report=1' % (self.absolute_url(), ppath))

    security.declareProtected(view_management_screens, 'formatDateTime')
    def formatDateTime(self, p_date):
        """ date is a DateTime object. This function returns a string 'dd month_name yyyy' """
        try: return p_date.strftime('%d/%m/%Y')
        except: return ''

    security.declareProtected(view_management_screens, 'generateFTCreationDate')
    def generateFTCreationDate(self, portal):
        """
            generate creation date
        """
        flist = [(f.bobobase_modification_time(), f) for f in self.list_zmi_templates(portal)]
        flist.sort()
        return flist[0][0]

    security.declareProtected(view_management_screens, 'reloadPortalForms')
    def reloadPortalForms(self, ppath, funmod=False, fmod=[], REQUEST=None):
        """ reload portal forms """
        portal = self.getPortal(ppath)
        fmods = convertToList(fmod)
        #modified forms
        for f in fmods:
            form_ob = self.get_zmi_template(f)
            fs_content = self.get_fs_template(form_ob.id, portal)
            try:
                form_ob.pt_edit(text=fs_content, content_type='')
            except Exception, error:
                print error
        #unmodified forms
        if funmod:
            modified, unmodified, list_diff = self.get_modified_forms(portal)
            all_forms = self.get_fs_forms(portal)
            for form_id, form_path in all_forms.items():
                if form_path not in [m.absolute_url(1) for m in modified]:
                    fs_content = self.get_fs_template(form_id, portal)
                    form_ob = self.get_zmi_template(form_path)
                    try:
                        if form_ob is None:
                            formstool_ob = portal.getFormsTool()
                            formstool_ob.manage_addTemplate(id=form_id, title='', file='')
                            form_ob = formstool_ob._getOb(form_id, None)
                        form_ob.pt_edit(text=fs_content, content_type='')
                        form_ob._p_changed = 1
                    except Exception, error:
                        print error

        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?ppath=%s&show_report=1' % (self.absolute_url(), ppath))


