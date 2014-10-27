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

# Python imports
import colorsys
import os.path
from cStringIO import StringIO
from PIL import Image

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseStatistic import manage_addStatistic
from BaseMatrixStatistic import BaseMatrixStatistic

class MatrixCssBarChartStatistic(BaseMatrixStatistic):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MatrixCssBarChartStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Matrix CSS Bar Chart Statistic"
    meta_label = "Matrix CSS Bar Chart Statistic"
    meta_sortorder = 311
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions."""
    icon_filename = "statistics/www/matrix_css_barchart_statistic.gif"

    security.declarePublic('getColors')
    def getPallete(self, numcolors):
        """Get a pallete of numcolors colors.

            The colors are a list of hexadecimal codes, e.g. '#f0b0d0'.
        """
        h, s, v = 0.01, 0.55, 0.95
        step = float(1 - h) / numcolors
        colors = []
        for i in range(numcolors):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = "%02x%02x%02x" % tuple([int(x*255) for x in h, s, v])
            colors.append(color)
            h += step
        return colors

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         unanswered=unanswered,
                         per_row_and_choice=per_row_and_choice,
                         colors=self.getPallete(len(self.question.choices) + 1))

    page = PageTemplateFile("zpt/matrix_css_barchart_statistics.zpt", globals())

    security.declarePrivate('add_to_excel')
    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific statistic type """
        import xlwt
        temp_folder = state['temp_folder']
        answers = state['answers']
        ws = state['ws']
        current_row = state['current_row']
        translator = self.getSite().getPortalTranslations()
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'www', 'barchart.png')
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        colors=self.getPallete(len(self.question.choices) + 1)

        #define Excel styles
        header_style = xlwt.easyxf('font: bold on; align: vert centre')
        normal_style = xlwt.easyxf('align: vert centre')

        #write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, header_style)
        current_row += 1

        for row in self.question.rows:
            r = self.question.rows.index(row)
            ws.write_merge(current_row,
                current_row+len(self.question.choices), 1, 1, row, header_style)
            for choice in self.question.choices:
                c = self.question.choices.index(choice)
                ws.write(current_row, 2, choice, header_style)
                width = int(per_row_and_choice[r][c][1]) * 2
                height = 12
                if width * height:
                    path = self.set_bitmap_props(file_path, width, height, temp_folder)
                    ws.insert_bitmap(path, current_row, 3, 0, 3)
                current_row += 1
            ws.write(current_row, 2, translator('Not answered'), header_style)
            width = int(unanswered[r][1]) * 2
            if width * height:
                path = self.set_bitmap_props(file_path, width, height, temp_folder)
                ws.insert_bitmap(path, current_row, 3, 0, 3)
            current_row += 2
        state['current_row'] = current_row

InitializeClass(MatrixCssBarChartStatistic)

def getStatistic():
    return MatrixCssBarChartStatistic
