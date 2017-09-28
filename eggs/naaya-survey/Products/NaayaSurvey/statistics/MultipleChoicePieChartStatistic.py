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

import urllib
import colorsys
from cStringIO import StringIO

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistic import BaseMultipleChoiceStatistic
import pygooglechart


class MultipleChoicePieChartStatistic(BaseMultipleChoiceStatistic):
    """Piechart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(
        MultipleChoicePieChartStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Pie Chart Statistic"
    meta_label = "Multiple Choice Pie Chart Statistic"
    meta_description = """Pie Chart for every choice"""
    meta_sortorder = 220
    icon_filename = 'statistics/www/multiplechoice_piechart_statistic.gif'

    security.declarePublic('get_chart')

    def get_chart(self, answers):
        """generate chart"""
        total, answered, unanswered, per_choice = self.calculate(self.question,
                                                                 answers)
        chart = pygooglechart.PieChart3D(600, 170)
        # data
        data = [i[1] for i in per_choice]
        data.append(unanswered[1])
        chart.add_data(data)
        # legend
        catalog = self.getPortalTranslations()
        legend = list(self.question.getChoices())
        legend.append(catalog('Not answered',
                              lang=self.gl_get_selected_language(), add=True))
        chart.set_pie_labels(legend)
        colors = []
        h, s, v = 0.01, 0.55, 0.95
        step = float(1 - h) / (len(self.question.getChoices()) + 1)
        for i in range(len(self.question.getChoices()) + 1):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = "%02x%02x%02x" % tuple([int(x*255) for x in r, g, b])
            colors.append(color)
            h += step
        chart.set_colours(colors)
        return chart

    security.declarePublic('render')

    def render(self, answers):
        """Render statistics as HTML code"""
        chart = self.get_chart(answers)
        return self.page(question=self.question,
                         chart_url=chart.get_url())

    page = PageTemplateFile("zpt/multiplechoice_piechart_statistics.zpt",
                            globals())

    security.declarePrivate('add_to_excel')

    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific
            statistic type """
        import xlwt
        temp_folder = state['temp_folder']
        answers = state['answers']
        ws = state['ws']
        current_row = state['current_row']
        chart_url = self.get_chart(answers).get_url()

        # define Excel styles
        style = xlwt.XFStyle()
        normalfont = xlwt.Font()
        headerfont = xlwt.Font()
        headerfont.bold = True
        style.font = headerfont

        # write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, style)
        current_row += 1
        file = urllib.urlopen(chart_url)
        file_string = StringIO(file.read())
        bitmap_props = self.get_bitmap_props(file_string, temp_folder)
        """ insert_bitmap (filename, row, column, delta_x, delta_y) """
        ws.insert_bitmap(bitmap_props['path'], current_row, 1, 0, 5)
        state['current_row'] = current_row + int(bitmap_props['height']/17) + 2

InitializeClass(MultipleChoicePieChartStatistic)


def getStatistic():
    return MultipleChoicePieChartStatistic
