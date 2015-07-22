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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from FormsTool import register_naaya_template

class NaayaPageTemplateFile(PageTemplateFile):
    def __init__(self, filename, _globals, form_id):
        super(NaayaPageTemplateFile, self).__init__(filename, _globals)
        self.form_id = form_id
        register_naaya_template(self, form_id)

    def pt_render(self, *args, **kwargs):
        try:
            site = self.getSite()
        except AttributeError, e:
            # there's no site in our acquisition context
            current_form = self
        else:
            forms_tool = site.getFormsTool()
            current_form = forms_tool._getOb(self.form_id, self)

        current_form = current_form.aq_self.__of__(self.aq_parent)

        return PageTemplate.pt_render(current_form, *args, **kwargs)
