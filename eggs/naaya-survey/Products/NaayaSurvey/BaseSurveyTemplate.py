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

# Python imports
import sys
from urllib import urlencode

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from DocumentTemplate.sequence import sort
from Globals import InitializeClass
from OFS.Folder import Folder
import Products
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import zLOG

# Naaya imports
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.NaayaWidgets.widgets import AVAILABLE_WIDGETS
from Products.NaayaWidgets.Widget import Widget, WidgetError, manage_addWidget
from Products.NaayaWidgets.widgets.LabelWidget import LabelWidget
from Products.NaayaWidgets.widgets.MultipleChoiceWidget import MultipleChoiceWidget
from Products.NaayaWidgets.widgets.ComboboxMatrixWidget import ComboboxMatrixWidget
from Products.NaayaWidgets.widgets.MatrixWidget import MatrixWidget
from Products.NaayaWidgets.widgets.TextAreaWidget import TextAreaWidget
from Products.NaayaWidgets.widgets.StringWidget import StringWidget
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES

# reports
from SurveyAttachment import SurveyAttachment, addSurveyAttachment
from SurveyReport import SurveyReport, manage_addSurveyReport
from statistics.BaseStatistic import manage_addStatistic
from statistics.SimpleTabularStatistic import SimpleTabularStatistic
from statistics.MultipleChoiceTabularStatistic import MultipleChoiceTabularStatistic
from statistics.MultipleChoiceCssBarChartStatistic import MultipleChoiceCssBarChartStatistic
from statistics.MultipleChoiceGoogleBarChartStatistic import MultipleChoiceGoogleBarChartStatistic
from statistics.MultipleChoicePieChartStatistic import MultipleChoicePieChartStatistic
from statistics.MatrixTabularStatistic import MatrixTabularStatistic
from statistics.MatrixCssBarChartStatistic import MatrixCssBarChartStatistic
from statistics.ComboboxMatrixTabularStatistic import ComboboxMatrixTabularStatistic
from statistics.TextAnswerListing import TextAnswerListing

WIDGETS = dict([(widget.meta_type, widget) for widget in AVAILABLE_WIDGETS])

class BaseSurveyTemplate(Folder, LocalPropertyManager):
    """Survey Template"""

    manage_options=(
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','ObjectManager_Contents.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'Security', 'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
        )

    _properties=()

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
        return (
            self.get_widget_meta_types() +
            self.get_report_meta_types() +
            self._get_meta_types_from_names(['Script (Python)',
                                             'Page Template'])+
            [{
            'name': "Naaya Survey Answer",
            'action': 'base_questionnaire_add_html',
            'permission': 'view',
            }]
        )

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
    security.declarePrivate('saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """Update properties"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        lang = kwargs.get('lang', self.get_selected_language())
        local_properties = filter(None, [x.get('id', None) for x in self.getLocalProperties()])
        # Update localized properties
        for local_property in local_properties:
            prop_value = kwargs.get(local_property, '')
            self.set_localpropvalue(local_property, lang, prop_value)
        # Update non-localized properties
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
                'meta_type': getattr(instance, 'meta_type', ''),
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

    security.declareProtected(view, 'getNonEmptyAttribute')
    def getNonEmptyAttribute(self, attr):
        """ Return the value of the first non empty <attr> local atribute."""
        return self.getLocalAttribute(attr, langFallback=True)

    #
    # Widget edit methods
    #
    security.declarePrivate('addWidget')
    def addWidget(self, REQUEST=None, title='', meta_type=None, **kwargs):
        """Add a widget.

            @param meta_type: metatype of the widget
        """
        err = []
        if not title:
            err.append('Field title is required')
        if not meta_type:
            err.append('Field type is required')

        if err:
            if REQUEST is None:
                raise ValueError('.'.join(err))
            self.setSessionErrorsTrans(err)
            self.setSession('title', title)
            self.setSession('meta_type', meta_type)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        widget_cls = WIDGETS[meta_type]
        return manage_addWidget(widget_cls,
                                self,
                                title=title,
                                REQUEST=REQUEST)

    security.declarePrivate('deleteItems')
    def deleteItems(self, ids=[], REQUEST=None):
        """ Delete items (e.g. widgets, reports) by ids"""
        if not ids:
            self.setSessionErrorsTrans('Please select one or more items to delete.')
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
                self.setSessionErrorsTrans('Error while deleting data.')
            else:
                self.setSessionInfoTrans('Item(s) deleted.')
        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declarePrivate('setSortOrder')
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        return True

    #
    # Bulk widgets methods
    #
    security.declareProtected(view, 'render')
    def render(self, mode='view', datamodel={}, **kwargs):
        """Render widgets"""
        widgets = self.getSortedWidgets()
        return '\n'.join([widget.render(mode=mode, datamodel=datamodel.get(widget.id, None), **kwargs)
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

    security.declareProtected(view, 'getSortedReports')
    def getSortedReports(self, sort_by='title'):
        """ """
        return sort(self.getReports(), ( (sort_by, 'cmp', 'asc'), ))

    security.declarePrivate('addReport')
    def addReport(self, title='', REQUEST=None, **kwargs):
        """Add a new report"""
        err = []
        if not title:
            err.append('Field title is required')

        if err:
            if REQUEST is None:
                raise ValueError('.'.join(err))
            self.setSessionErrorsTrans(err)
            self.setSession('title', title)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        report_id = manage_addSurveyReport(self, title=title, REQUEST=REQUEST)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        return report_id

    security.declarePrivate('generateFullReport')
    def generateFullReport(self, title='', REQUEST=None):
        """Generate a full report"""
        if not title:
            if REQUEST is None:
                raise ValueError('Field title is required')
            self.setSessionErrorsTrans('Field title is required')
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        report_id = manage_addSurveyReport(self, title=title)
        report = self._getOb(report_id)
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

            elif isinstance(question, ComboboxMatrixWidget):
                stat_classes.extend([ComboboxMatrixTabularStatistic])
            elif isinstance(question, MatrixWidget):
                stat_classes.extend([MatrixTabularStatistic,
                                     MatrixCssBarChartStatistic])

            elif isinstance(question, StringWidget) or isinstance(question, TextAreaWidget):
                stat_classes.extend([TextAnswerListing])

            else:
                stat_classes.extend([SimpleTabularStatistic])

            for stat_class in stat_classes:
                manage_addStatistic(stat_class,
                                    report,
                                    question=question,
                                    sortorder=sortorder)
                sortorder += 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        return report_id

    #
    # Attachments
    #
    security.declareProtected(view, 'getAttachments')
    def getAttachments(self):
        """ """
        return self.objectValues([SurveyAttachment.meta_type])

    security.declareProtected(view, 'getReports')
    def getSortedAttachments(self, sort_by='title'):
        """ """
        return sort(self.getAttachments(), ( (sort_by, 'cmp', 'asc'), ))

    security.declarePrivate('addAttachment')
    def addAttachment(self, title='', REQUEST=None, **kwargs):
        """Add an attachment"""
        result = addSurveyAttachment(self, title=title, REQUEST=REQUEST, **kwargs)
        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        return result

    #
    # Macros
    #
    security.declareProtected(view, 'base_edit_attachments_html')
    base_edit_attachments_html = PageTemplateFile('zpt/base_surveytemplate_edit_attachments', globals())

    security.declareProtected(view, 'base_edit_questions_html')
    base_edit_questions_html = PageTemplateFile('zpt/base_surveytemplate_edit_questions', globals())

    security.declareProtected(view, 'base_edit_reports_html')
    base_edit_reports_html = PageTemplateFile('zpt/base_surveytemplate_edit_reports', globals())

InitializeClass(BaseSurveyTemplate)
