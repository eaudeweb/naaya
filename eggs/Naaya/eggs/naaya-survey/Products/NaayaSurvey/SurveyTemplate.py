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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Cristian Ciupitu, Eau de Web

# Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaCore.managers.utils import genObjectId, genRandomId

from BaseSurveyTemplate import BaseSurveyTemplate
from permissions import PERMISSION_MANAGE_SURVEYTEMPLATE

def manage_addSurveyTemplate(context, id="", title="SurveyTemplate", REQUEST=None, **kwargs):
    """
    ZMI method that creates an object of this type.
    """
    if not id:
        id = genObjectId(title)

    idSuffix = ''
    while id+idSuffix in context.objectIds():
        idSuffix = genRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = REQUEST and REQUEST.form.get('lang', None)
    lang = lang or kwargs.get('lang', context.gl_get_selected_language())

    ob = SurveyTemplate(id, lang=lang, title=title)
    context.gl_add_languages(ob)
    context._setObject(id, ob)
    if REQUEST:
        return context.manage_main(context, REQUEST, update_menu=1)
    return id

class SurveyTemplate(BaseSurveyTemplate):
    """Survey Template"""

    meta_type = 'Naaya Survey Template'
    _constructors = (manage_addSurveyTemplate,)
    icon = 'misc_/NaayaSurvey/SurveyTemplate.gif'
    security = ClassSecurityInfo()

    def __init__(self, id, lang=None, **kwargs):
        BaseSurveyTemplate.__init__(self, id, lang, **kwargs)

    #
    # Site pages
    #
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'edit_html')
    edit_html = PageTemplateFile('zpt/surveytemplate_edit', globals())

    # TODO: add edit_attachments_html

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'edit_questions_html')
    edit_questions_html = PageTemplateFile('zpt/surveytemplate_edit_questions', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'edit_reports_html')
    edit_reports_html = PageTemplateFile('zpt/surveytemplate_edit_reports', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'preview_html')
    preview_html = PageTemplateFile('zpt/surveytemplate_preview', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'index_html')
    index_html = edit_questions_html

    #
    # change the security of the inherited methods
    #
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'saveProperties')
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'addWidget')
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'deleteItems')
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'setSortOrder')
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'addReport')
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'generateFullReport')
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'addAttachment')

InitializeClass(SurveyTemplate)
