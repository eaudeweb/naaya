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
import os.path
from cStringIO import StringIO
from PIL import Image

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistic import BaseMultipleChoiceStatistic

class MultipleChoiceCssBarChartStatistic(BaseMultipleChoiceStatistic):
    """Barchart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceCssBarChartStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice CSS Bar Chart Statistic"
    meta_label = "Multiple Choice CSS Bar Chart Statistic"
    meta_description = """Bar chart for every choice"""
    meta_sortorder = 211
    icon_filename = 'statistics/www/multiplechoice_css_barchart_statistic.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered,
                         per_choice=per_choice)

    page = PageTemplateFile("zpt/multiplechoice_css_barchart_statistics.zpt", globals())

    security.declarePrivate('add_to_excel')
    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific statistic type """
        import xlwt
        temp_folder = state['temp_folder']
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

        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'www', 'barchart.png')
        choice_count = 0
        for choice in self.question.getChoices():
            ws.write(current_row, 3, '%s (%s)'
                % (choice, per_choice[choice_count][0]), normal_style)
            width = int(per_choice[choice_count][1])
            height = 12
            if width * height:
                path = self.set_bitmap_props(file_path, width, height, temp_folder)
                #syntax: insert_bitmap(filename, row, column, delta_x, delta_y)
                ws.insert_bitmap(path, current_row, 1, 0, 3)
            choice_count += 1
            current_row += 1
        ws.write(current_row, 3, translator('Not answered') + ' (%s)'
            % unanswered[0], normal_style)
        width = int(unanswered[1])
        height = 12
        if width * height:
            path = self.set_bitmap_props(file_path, width, height, temp_folder)
            ws.insert_bitmap(path, current_row, 1, 0, 3)

        state['current_row'] = current_row + 1

InitializeClass(MultipleChoiceCssBarChartStatistic)

def getStatistic():
    return MultipleChoiceCssBarChartStatistic
