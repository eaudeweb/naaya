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

# Zope imports
from DateTime import DateTime
from OFS.Folder import Folder
from OFS.Traversable import path2url
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from ZPublisher.HTTPRequest import FileUpload
from zLOG import LOG, INFO

# Products import
from Products.ExtFile.ExtFile import manage_addExtFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.managers.utils import utils

from permissions import PERMISSION_VIEW_ANSWERS

gUtil = utils()

def manage_addSurveyAnswer(context, datamodel, respondent=None, REQUEST=None):
    """ Constructor for SurveyAnswer"""
    global gUtil

    if respondent is None:
        respondent = REQUEST.AUTHENTICATED_USER.getUserName()

    # calculate an available id
    while True:
        idSuffix = gUtil.utGenRandomId()
        id = datamodel['id'] = 'answer_%s' % (idSuffix, )
        try:
            ob = SurveyAnswer(id, datamodel, respondent)
            context._setObject(id, ob)
        except:
            LOG('NaayaSurvey - SurveyAnswer', INFO, 'manage_addSurveyAnswer: answer with id %s already exists! Trying with another one!' % id)
            continue
        break

    ob = context._getOb(id)

    # handle files
    for key, value in datamodel.items():
        if isinstance(value, FileUpload):
            ob.handle_upload(key, value)

    # index the new object
    catalog_tool = context.getCatalogTool()
    catalog_tool.catalog_object(ob, path2url(ob.getPhysicalPath()))

    return id


class SurveyAnswer(Folder):
    """ Class used to store survey answers"""
    meta_type = "Naaya Survey Answer"
    meta_label = "Survey Answer"
    icon = 'misc_/NaayaSurvey/NySurveyAnswer.gif'

    _constructors = (manage_addSurveyAnswer,)
    _properties=()
    all_meta_types = ()
    manage_options=(
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','ObjectManager_Contents.stx')},
     )

    security = ClassSecurityInfo()

    def __init__(self, id, datamodel, respondent):
        Folder.__init__(self, id)
        self.add_properties(datamodel)
        self.respondent = respondent

    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'add_properties')
    def add_properties(self, datamodel):
        for key, value in datamodel.items():
            if isinstance(value, FileUpload):
                continue # Handled somewhere else
            setattr(self, key, value)

    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'handle_upload')
    def handle_upload(self, id, attached_file):
        if id in self.objectIds():
            self.manage_delObjects([id,])
        manage_addExtFile(self, id, title=attached_file.filename,
                          file=attached_file)

    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'getAnswerForQuestionId')
    def getAnswerForQuestionId(self, question_id):
        if hasattr(self, question_id):
            return getattr(self, question_id)
        return None

    # The special permission PERMISSION_VIEW_ANSWERS is used instead of the
    # regular "view" permission because otherwise, by default, all users
    # (including anonymous ones) can see all answers. Also setting the view
    # permission for each SurveyAnswer wouldn't be practical.
    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'index_html')
    index_html = PageTemplateFile('zpt/surveyanswer_index', globals())
