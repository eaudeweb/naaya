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
# Alex Morega, Eau de Web

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaWidgets.widgets.RadioMatrixWidget import RadioMatrixWidget
from Products.NaayaWidgets.widgets.ComboboxMatrixWidget import ComboboxMatrixWidget

from BaseStatistic import manage_addStatistic, BaseStatistic

class ComboboxMatrixTabularStatistic(BaseStatistic):
    """Table with the count and percent of answered and unanswered questions,
        diveded per row and choice. It should be used for combobox matrix questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(
        ComboboxMatrixTabularStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Combobox Matrix Tabular Statistic"
    meta_label = "Combobox Matrix Tabular Statistic"
    meta_sortorder = 320
    meta_description = """Table with the count and percent of answered and
        unanswered questions, diveded per row and choice. It should be used
        for combobox matrix questions."""
    icon_filename = 'statistics/www/matrix_tabular_statistic.gif'

    def __init__(self, id, question, lang=None, **kwargs):
        if not isinstance(question, ComboboxMatrixWidget):
            raise TypeError('Unsupported question type')
        BaseStatistic.__init__(self, id, question, lang=lang, **kwargs)

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered, per_choice)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        per_row_and_choice_count = [[[0
            for v in question.values]
            for c in question.choices]
            for r in question.rows]
        unanswered_count = [[0
            for c in question.choices]
            for r in question.rows]
        for answer in answers:
            total += 1
            answer = answer.get(w_id)
            if answer is None:
                for r in range(len(question.rows)):
                    for c in range(len(question.choices)):
                        unanswered_count[r][c] += 1
                continue
            for r, per_row_choices in enumerate(answer):
                for c, value in enumerate(per_row_choices):
                    if value:
                        per_row_and_choice_count[r][c][value] += 1
                    else:
                        unanswered_count[r][c] += 1

        if total:
            unanswered_stats = [[(x, 100.0 * x / total)
                for x in row]
                for row in unanswered_count]
            per_row_and_choice_stats = [[[(i, 100.0 * i / total)
                for i in per_value_count]
                for per_value_count in per_choice_count]
                for per_choice_count in per_row_and_choice_count]
        else:
            unanswered_stats = [[(0, 0.0)
                for x in row]
                for row in unanswered_count]
            per_row_and_choice_stats = [[[(0, 0.0)
                for i in per_value_count]
                for per_value_count in per_choice_count]
                for per_choice_count in per_row_and_choice_count]

        return (total, unanswered_stats, per_row_and_choice_stats)

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         unanswered=unanswered,
                         per_row_and_choice=per_row_and_choice)

    page = PageTemplateFile("zpt/combobox_matrix_tabular_statistics.zpt", globals())

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
        italic_style = xlwt.easyxf('align: vert centre; font: italic on')

        #write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, header_style)
        current_row += 1
        ws.write(current_row, 1, translator('row'), italic_style)
        ws.write(current_row, 2, translator('value'), italic_style)
        current_col = 3
        for choice in self.question.choices:
            ws.write(current_row, current_col, choice, header_style)
            current_col += 1
        current_row += 1
        for row in self.question.rows:
            r = self.question.rows.index(row)
            current_col = 1
            ws.write_merge(current_row,
                current_row+len(self.question.values), 1, 1, row, header_style)
            for value in self.question.values:
                v = self.question.values.index(value)
                current_col = 2
                ws.write(current_row, current_col, value, header_style)
                current_col += 1
                for statistic in per_row_and_choice[r]:
                    ws.write(current_row, current_col, '%u (%.2f%%)'
                        % (statistic[v][0], round(statistic[v][1], 2)), normal_style)
                    current_col += 1
                current_row += 1
            current_col = 2
            ws.write(current_row, current_col, translator('Not answered'), header_style)
            current_col += 1
            for statistic in unanswered[r]:
                ws.write(current_row, current_col, '%u (%.2f%%)'
                    % (statistic[0], round(statistic[1], 2)), normal_style)
                current_col += 1
            current_row += 1

        state['current_row'] = current_row + 1

InitializeClass(ComboboxMatrixTabularStatistic)

def getStatistic():
    return ComboboxMatrixTabularStatistic
