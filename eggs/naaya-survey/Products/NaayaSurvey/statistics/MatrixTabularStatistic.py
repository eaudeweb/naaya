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
from BaseMatrixStatistic import BaseMatrixStatistic

class MatrixTabularStatistic(BaseMatrixStatistic):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MatrixTabularStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Matrix Tabular Statistic"
    meta_label = "Matrix Tabular Statistic"
    meta_sortorder = 300
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions."""
    icon_filename = 'statistics/www/matrix_tabular_statistic.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         unanswered=unanswered,
                         per_row_and_choice=per_row_and_choice)

    page = PageTemplateFile("zpt/matrix_tabular_statistics.zpt", globals())

    security.declarePrivate('add_to_excel')
    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific statistic type """
        import xlwt
        answers = state['answers']
        ws = state['ws']
        current_row = state['current_row']
        translator = self.getSite().getPortalTranslations()
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)

        #define Excel styles
        header_style = xlwt.easyxf('font: bold on; align: vert centre')
        normal_style = xlwt.easyxf('align: vert centre')

        #write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, header_style)
        current_row += 1
        current_col = 2
        for choice in self.question.choices:
            ws.write(current_row, current_col, choice, header_style)
            current_col += 1
        ws.write(current_row, current_col, translator('Not answered'), header_style)
        current_row += 1

        for row in self.question.rows:
            r = self.question.rows.index(row)
            ws.write(current_row, 1, row, header_style)
            current_col = 2
            for statistics in per_row_and_choice[r]:
                ws.write(current_row, current_col, '%u (%.2f%%)'
                    % (statistics[0], round(statistics[1], 2)), normal_style)
                current_col += 1
            ws.write(current_row, current_col, '%u (%.2f%%)'
                % (unanswered[r][0], round(unanswered[r][1], 2)), normal_style)
            current_row += 1
        state['current_row'] = current_row

InitializeClass(MatrixTabularStatistic)

def getStatistic():
    return MatrixTabularStatistic
