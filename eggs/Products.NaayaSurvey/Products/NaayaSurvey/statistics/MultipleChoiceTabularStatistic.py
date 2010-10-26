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

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseStatistic import manage_addStatistic
from BaseMultipleChoiceStatistic import BaseMultipleChoiceStatistic

class MultipleChoiceTabularStatistic(BaseMultipleChoiceStatistic):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for multiple choice questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceTabularStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Tabular Statistic"
    meta_label = "Multiple Choice Tabular Statistic"
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for multiple choice questions."""
    meta_sortorder = 200
    icon_filename = 'statistics/www/multiplechoice_tabular_statistic.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered,
                         per_choice=per_choice)

    page = PageTemplateFile("zpt/multiplechoice_tabular_statistics.zpt", globals())

    security.declarePrivate('add_to_excel')
    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific statistic type """
        import xlwt
        answers = state['answers']
        ws = state['ws']
        current_row = state['current_row']
        translator = self.getSite().getPortalTranslations()
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)

        #define Excel styles
        header_style = xlwt.easyxf('font: bold on; align: vert centre')
        normal_style = xlwt.easyxf('align: vert centre')

        #write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, header_style)
        current_row += 1
        ws.write(current_row, 1, translator('Choice'), header_style)
        ws.write(current_row, 2, translator('Count'), header_style)
        ws.write(current_row, 3, translator('Percent'), header_style)
        current_row += 1
        for choice in self.question.getChoices():
            c = self.question.getChoices().index(choice)
            ws.write(current_row, 1, choice, header_style)
            ws.write(current_row, 2, per_choice[c][0], normal_style)
            ws.write(current_row, 3, '%.2f%%'
                % (round(per_choice[c][1], 2), ), normal_style)
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
        state['current_row'] = current_row + 1

InitializeClass(MultipleChoiceTabularStatistic)

def getStatistic():
    return MultipleChoiceTabularStatistic
