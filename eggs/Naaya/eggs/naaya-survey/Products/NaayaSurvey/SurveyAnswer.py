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
from zope import interface
from zope.event import notify

# Products import
from Products.ExtFile.ExtFile import manage_addExtFile
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED_MSG
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaBase.NyProperties import NyProperties

from permissions import PERMISSION_VIEW_ANSWERS, PERMISSION_EDIT_ANSWERS
from interfaces import INySurveyAnswer, INySurveyAnswerAddEvent

gUtil = utils()

def manage_addSurveyAnswer(context, datamodel, respondent=None, draft=False,
                           REQUEST=None, id=None):
    """ Constructor for SurveyAnswer"""
    global gUtil

    if respondent is None and REQUEST is not None:
            respondent = REQUEST.AUTHENTICATED_USER.getUserName()

    if not id or id in context.objectIds():
        # calculate an available id
        while True:
            idSuffix = gUtil.utGenRandomId()
            id = 'answer_%s' % (idSuffix, )
            if id not in context.objectIds():
                break

    ob = SurveyAnswer(id, respondent, draft)
    context._setObject(id, ob)
    ob = context._getOb(id)

    ob.set_datamodel(datamodel)
    # handle files
    for key, value in datamodel.items():
        if isinstance(value, FileUpload):
            ob.handle_upload(key, value)

    notify(NySurveyAnswerAddEvent(ob))

    return id


class SurveyAnswer(Folder, NyProperties):
    """ Class used to store survey answers"""

    interface.implements(INySurveyAnswer)

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

    def __init__(self, id, respondent, draft):
        Folder.__init__(self, id)
        NyProperties.__init__(self)
        self.respondent = respondent
        self.draft = bool(draft)
        self.modification_time = DateTime()

    security.declarePrivate('set_datamodel')
    def set_datamodel(self, datamodel):
        for key, value in datamodel.items():
            self.set_property(key, value)

    def set_property(self, key, value):
        if isinstance(value, FileUpload):
            return # Handle somewhere else

        widget = self.getWidget(key)
        if widget.localized:
            for lang in self.gl_get_languages():
                lang_value = value.get(lang, None)
                # don't add a value if lang_value is empty
                # easier to test if localized value is empty
                if lang_value:
                    self._setLocalPropValue(key, lang, lang_value)
        else:
            setattr(self, key, value)

    security.declarePrivate('handle_upload')
    def handle_upload(self, id, attached_file):
        if id in self.objectIds():
            self.manage_delObjects([id,])
        manage_addExtFile(self, id, title=attached_file.filename,
                          file=attached_file)

    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'getDatamodel')
    def getDatamodel(self):
        """ """
        return dict([(widget.id, self.get(widget.id))
                     for widget in self.getSortedWidgets()])

    def get(self, key, default=None, lang=None):
        """Returns the value for key, else default

        For localized widgets it returns a dict unless a lang is specified
        """
        if key in self._local_properties:
            if lang is None:
                ret = {}
                for lang in self.gl_get_languages():
                    try:
                        ret[lang] = self.getLocalProperty(key, lang)
                    except:
                        ret[lang] = default
                return ret
            else:
                try:
                    return self.getLocalProperty(key, lang)
                except:
                    return default
        else:
            return getattr(self.aq_base, key, default)


    # The special permission PERMISSION_VIEW_ANSWERS is used instead of the
    # regular "view" permission because otherwise, by default, all users
    # (including anonymous ones) can see all answers. Also setting the view
    # permission for each SurveyAnswer wouldn't be practical.

    _index_html = NaayaPageTemplateFile('zpt/surveyanswer_index',
                    globals(), 'NaayaSurvey.surveyanswer_index')
    def index_html(self,REQUEST=None):
        """ Return the answer index if the current user
        is the respondent or has permission to view answers """

        if REQUEST:
            if self.respondent == REQUEST.AUTHENTICATED_USER.getUserName():
                return self._index_html()

        if self.checkPermission(PERMISSION_VIEW_ANSWERS):
            return self._index_html()
        else:
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

    def answer_values(self, REQUEST=None, **kwargs):
        """ Return values as list.
        """
        datamodel=self.getDatamodel()
        widgets = self.getSortedWidgets()
        atool = self.getSite().getAuthenticationTool()
        ut = utils()
        respondent = atool.getUserFullNameByID(self.respondent)
        res = [respondent]
        for widget in widgets:
            res.append(widget.get_value(
                datamodel=datamodel.get(widget.id, None), **kwargs))
        return res

    def is_draft(self):
        return getattr(self, 'draft', False)

    security.declareProtected(PERMISSION_EDIT_ANSWERS, 'deleteSurveyAnswer')
    def deleteSurveyAnswer(self, REQUEST=None):
        """ """
        survey = self.aq_inner.aq_parent
        survey.deleteAnswer(self.id)

        if REQUEST:
            REQUEST.RESPONSE.redirect(survey.absolute_url())

class NySurveyAnswerAddEvent(object):
    """ """
    interface.implements(INySurveyAnswerAddEvent)

    def __init__(self, context):
        self.context = context
