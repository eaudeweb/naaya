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

# Python imports
import sys
from urllib import urlencode

# Zope imports
import zLOG
import Products
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Globals import InitializeClass
from DocumentTemplate.sequence import sort
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.NaayaCore.managers.utils import utils
from Products.NaayaWidgets.widgets import AVAILABLE_WIDGETS
from Products.NaayaWidgets.Widget import Widget, WidgetError
from Products.NaayaWidgets.widgets.LabelWidget import LabelWidget
from Products.NaayaWidgets.widgets.MultipleChoiceWidget import MultipleChoiceWidget
from Products.NaayaWidgets.widgets.MatrixWidget import MatrixWidget
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES

# reports
from SurveyReport import SurveyReport, manage_addSurveyReport
from statistics.BaseStatistic import manage_addStatistic
from statistics.SimpleTabularStatistic import SimpleTabularStatistic
from statistics.MultipleChoiceTabularStatistic import MultipleChoiceTabularStatistic
from statistics.MultipleChoiceCssBarChartStatistic import MultipleChoiceCssBarChartStatistic
from statistics.MultipleChoiceGoogleBarChartStatistic import MultipleChoiceGoogleBarChartStatistic
from statistics.MultipleChoicePieChartStatistic import MultipleChoicePieChartStatistic
from statistics.MatrixTabularStatistic import MatrixTabularStatistic
from statistics.MatrixCssBarChartStatistic import MatrixCssBarChartStatistic

from constants import PERMISSION_MANAGE_SURVEYTEMPLATE

def manage_addSurveyTemplate(context, id="", title="SurveyTemplate", REQUEST=None, **kwargs):
    """
    ZMI method that creates an object of this type.
    """
    util = utils()
    if not id:
        id = util.utGenObjectId(title)

    idSuffix = ''
    while id+idSuffix in context.objectIds():
        idSuffix = util.utGenRandomId(p_length=4)
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

class SurveyTemplate(Folder, LocalPropertyManager):
    """Survey Template"""

    meta_type = 'Naaya Survey Template'

    manage_options=(
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','ObjectManager_Contents.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'Security', 'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
        )

    _constructors = (manage_addSurveyTemplate,)

    _properties=()

    icon = 'misc_/NaayaSurvey/SurveyTemplate.gif'

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    description = LocalProperty('description')

    def _get_meta_types_from_names(self, meta_type_names):
        """Return the meta_type objects for meta_type_names"""
        meta_types = []
        for meta_type in Products.meta_types:
            if meta_type['name'] in meta_type_names:
                meta_types.append(meta_type)
        return meta_types

    def get_widget_meta_types(self):
        """ """
        return self._get_meta_types_from_names([w.meta_type for w in AVAILABLE_WIDGETS])

    def get_report_meta_types(self):
        """ """
        return self._get_meta_types_from_names([SurveyReport.meta_type])

    def all_meta_types(self, interfaces=None):
        """ What can you put inside me? """
        return self.get_widget_meta_types() + self.get_report_meta_types()

    def __init__(self, id, lang=None, **kwargs):
        Folder.__init__(self, id=id)
        self.set_localproperty('title', 'string', lang)
        self.set_localproperty('description', 'text', lang)
        self.saveProperties(lang=lang, **kwargs)

    #
    # global methods used in naaya site context
    #
    def _object_add_language(self, language, **kwargs):
        for doc in self.objectValues():
            doc.add_language(language)

    def _object_del_language(self, language, **kwargs):
        for doc in self.objectValues():
            doc.del_language(language)

    #
    # Self edit methods
    #
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ Update type properties"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        local_properties = filter(None, [x.get('id', None) for x in self.getLocalProperties()])
        # Update local properties
        lang = kwargs.get('lang', self.get_selected_language())
        for local_property in local_properties:
            prop_value = kwargs.get(local_property, '')
            self.set_localpropvalue(local_property, lang, prop_value)
        kwargs = dict([(key, value) for key, value in kwargs.items()
                       if key not in local_properties])
        self.manage_changeProperties(**kwargs)
        if REQUEST:
            query = {'lang': lang}
            query = urlencode(query)
            REQUEST.RESPONSE.redirect('%s/edit_html?%s' % (self.absolute_url(), query))
        return True

    #
    # Widget read methods
    #
    security.declareProtected(view, 'getWidgetTypes')
    def getWidgetTypes(self):
        """What widgets can I add inside this?"""
        types = self.get_widget_meta_types()
        for widget_type in types:
            instance = widget_type.get('instance', None)
            widget_type.update({
                'meta_label': getattr(instance, 'meta_label', ''),
                'meta_description': getattr(instance, 'meta_description', ''),
            })
        return types

    security.declareProtected(view, 'getWidgetTypesAsMatrix')
    def getWidgetTypesAsMatrix(self, cols=3):
        """ Return widget types as a matrix with cols columns"""
        widget_types = self.getWidgetTypes()
        rows = len(widget_types) / cols
        rows += len(widget_types) % cols and 1
        return [[
            x for i, x in enumerate(widget_types) if i / cols == j]
            for j in range(rows)
        ]

    security.declareProtected(view, 'getWidget')
    def getWidget(self, widget_id='', default=None, **kwargs):
        """ Return widget by id"""
        if not widget_id:
            return default
        return self._getOb(widget_id, default)

    security.declareProtected(view, 'getWidgets')
    def getWidgets(self):
        """ """
        return self.objectValues([w.meta_type for w in AVAILABLE_WIDGETS])

    security.declareProtected(view, 'getSortedWidgets')
    def getSortedWidgets(self, sort_by='sortorder'):
        """ Return sorted widget"""
        return sort(self.getWidgets(), ( (sort_by, 'cmp', 'asc'), ))

    #
    # Widget edit methods
    #
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'addWidget')
    def addWidget(self, REQUEST, title='', add_action='', **kwargs):
        """ Add a new widget"""
        err = []
        if not title:
            err.append('Field title is required')
        if not add_action:
            err.append('Field type is required')

        if err:
            self.setSessionErrors(err)
            self.setSession('title', title)
            self.setSession('add_action', add_action)
            redirect_url = '%s/index_html' % self.absolute_url()
        else:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            redirect_url = '%s/%s?%s' % (self.absolute_url(), add_action, urlencode({'title': title}))
        REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'deleteItems')
    def deleteItems(self, ids=[], REQUEST=None):
        """ Delete items (e.g. widgets, reports) by ids"""
        if not ids:
            self.setSessionErrors(['Please select one or more items to delete.'])
        else:
            try:
                if isinstance(self._getOb(ids[0]), AVAILABLE_WIDGETS):
                    # if we're deleting questions, delete the 
                    # corresponding statistics too
                    for report in self.getReports():
                        statistic_ids = [stat.id for stat in report.getStatistics() if stat.question.id in ids]
                        report.manage_delObjects(statistic_ids)
                self.manage_delObjects(ids)
            except:
                err = sys.exc_info()
                zLOG.LOG('Naaya Survey Tool', zLOG.ERROR,
                         'Could not delete items', error=err)
                self.setSessionErrors(['Error while delete data.'])
            else:
                self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'setSortOrder')
    def setSortOrder(self, REQUEST=None, **kwargs):
        """ Bulk update widgets sort order"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        for key, value in kwargs.items():
            widget = self._getOb(key, None)
            if widget is None or not isinstance(widget, Widget):
                continue
            widget.saveProperties(sortorder=value)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        return True

    #
    # Bulk widgets methods
    #
    security.declareProtected(view, 'render')
    def render(self, mode='view', datamodel={}, **kwargs):
        """ Render widgets """
        widgets = self.getSortedWidgets()
        return '\n'.join([widget.render(mode=mode, datamodel=datamodel, **kwargs)
                          for widget in widgets])


    #
    # Reports
    #
    security.declareProtected(view, 'getReport')
    def getReport(self, report_id='', default=None, **kwargs):
        """ Return widget by id"""
        if not report_id:
            return default
        return self._getOb(report_id, default)

    security.declareProtected(view, 'getReports')
    def getReports(self):
        """ """
        return self.objectValues([SurveyReport.meta_type])

    security.declareProtected(view, 'getReports')
    def getSortedReports(self, sort_by='title'):
        """ """
        return sort(self.getReports(), ( (sort_by, 'cmp', 'asc'), ))

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'addReport')
    def addReport(self, title='', add_action='', REQUEST=None, **kwargs):
        """Add a new report"""
        if not REQUEST:
            return
        err = []
        if not title:
            err.append('Field title is required')

        if err:
            self.setSessionErrors(err)
            self.setSession('title', title)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        else:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            manage_addSurveyReport(self, title=title, REQUEST=REQUEST)
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'generateFullReport')
    def generateFullReport(self, id='full_report', title='Full report', REQUEST=None):
        """Generate a full report"""
        if self._getOb(id, None) is not None:
            self.manage_delObjects([id])
        id = manage_addSurveyReport(self, id, title)
        report = self._getOb(id)
        sortorder = 1
        for question in self.getSortedWidgets():
            stat_classes = []
            if isinstance(question, LabelWidget):
                pass
            elif isinstance(question, MultipleChoiceWidget):
                stat_classes.extend([MultipleChoiceTabularStatistic,
                                     MultipleChoiceCssBarChartStatistic,
                                     MultipleChoiceGoogleBarChartStatistic,
                                     MultipleChoicePieChartStatistic])
            elif isinstance(question, MatrixWidget):
                stat_classes.extend([MatrixTabularStatistic,
                                     MatrixCssBarChartStatistic])
            else:
                stat_classes.extend([SimpleTabularStatistic])

            for stat_class in stat_classes:
                manage_addStatistic(stat_class,
                                    report,
                                    question=question,
                                    sortorder=sortorder)
                sortorder += 1

    #
    # Site pages
    #
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'edit_html')
    edit_html = PageTemplateFile('zpt/surveytemplate_edit', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'edit_questions_html')
    edit_questions_html = PageTemplateFile('zpt/surveytemplate_edit_questions', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'edit_reports_html')
    edit_reports_html = PageTemplateFile('zpt/surveytemplate_edit_reports', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'preview_html')
    preview_html = PageTemplateFile('zpt/surveytemplate_preview', globals())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'index_html')
    index_html = edit_questions_html


InitializeClass(SurveyTemplate)
