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
# Cristian Ciupitu, Eau de Web

import xlwt

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaWidgets.widgets.LabelWidget import LabelWidget

from BaseStatistic import BaseStatistic, manage_addStatistic

class SimpleTabularStatistic(BaseStatistic):
    """Table with the count and percent of answered and unanswered questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(SimpleTabularStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Simple Tabular Statistic"
    meta_label = "Simple Tabular Statistic"
    meta_description = """Table with the count and percent of answered and unanswered questions."""
    meta_sortorder = 100
    icon_filename = 'statistics/www/simple_tabular_statistic.gif'

    def __init__(self, id, question, lang=None, **kwargs):
        if isinstance(question, LabelWidget):
            raise TypeError('Unsupported question type')
        BaseStatistic.__init__(self, id, question, lang=lang, **kwargs)

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        for answer in answers:
            val = answer.get(w_id)
            if val:
                answered_count += 1
            total += 1

        unanswered_count = total - answered_count
        if total:
            answered_percent = 100.0 * answered_count / total
            unanswered_percent = 100.0 * unanswered_count / total
        else:
            answered_percent = unanswered_percent = 0
        return (total,
                (answered_count, answered_percent),
                (unanswered_count, unanswered_percent))

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered)

    page = PageTemplateFile("zpt/simple_tabular_statistics.zpt", globals())

    security.declarePrivate('add_to_excel')
    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific statistic type """
        answers = state['answers']
        ws = state['ws']
        current_row = state['current_row']
        translator = self.getSite().getPortalTranslations()
        total, answered, unanswered = self.calculate(self.question, answers)

        #define Excel styles
        header_style = xlwt.easyxf('font: bold on; align: vert centre')
        normal_style = xlwt.easyxf('align: vert centre')

        #write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, header_style)
        current_row += 1
        ws.write(current_row, 2, translator('Count'), header_style)
        ws.write(current_row, 3, translator('Percent'), header_style)
        current_row += 1
        ws.write(current_row, 1, translator('Answered'), header_style)
        ws.write(current_row, 2, answered[0], normal_style)
        ws.write(current_row, 3, '%.2f%%'
            % (round(answered[1], 2), ), normal_style)
        current_row += 1
        ws.write(current_row, 1, translator('Not answered'), header_style)
        ws.write(current_row, 2, unanswered[0], normal_style)
        ws.write(current_row, 3, '%.2f%%'
            % (round(unanswered[1], 2), ), normal_style)
        current_row += 1
        ws.write(current_row, 1, translator('Total'), header_style)
        ws.write(current_row, 2, total, normal_style)
        ws.write(current_row, 3, '100%%', normal_style)
        current_row += 1

        state['current_row'] = current_row

InitializeClass(SimpleTabularStatistic)

def getStatistic():
    return SimpleTabularStatistic
