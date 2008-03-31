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

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistic import BaseMultipleChoiceStatistic
import pygooglechart

class MultipleChoiceGoogleBarChartStatistic(BaseMultipleChoiceStatistic):
    """Barchart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceGoogleBarChartStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Google Bar Chart Statistic"
    meta_label = "Multiple Choice Google Bar Chart Statistic"
    meta_description = """Bar chart for every choice"""
    meta_sortorder = 210

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        chart = pygooglechart.GroupedHorizontalBarChart(500, 23 + (len(self.question.getChoices())+1) * 22)
        chart.set_bar_width(5)
        # data
        data = [i[0] for i in per_choice]
        data.append(unanswered[0])
        for x in data:
            chart.add_data([x, 0]) # the 0 is an ugly hack
        # legend
        legend = list(self.question.getChoices())
        legend.append(self.getPortalTranslations().translate('', 'Not answered'))
        chart.set_legend(legend)
        # axis
        chart.set_axis_range(pygooglechart.Axis.BOTTOM, *chart.data_x_range())
        # colors
        colors = []
        h, s, v = 0.01, 0.55, 0.95
        step = float(1 - h) / (len(self.question.getChoices()) + 1)
        for i in range(len(self.question.getChoices()) + 1):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = "%02x%02x%02x" % tuple([int(x*255) for x in h, s, v])
            colors.append(color)
            h += step
        chart.set_colours(colors)

        return self.page(question=self.question,
                         chart_url=chart.get_url())

    page = PageTemplateFile("zpt/multiplechoice_google_barchart_statistics.zpt", globals())

InitializeClass(MultipleChoiceGoogleBarChartStatistic)

def getStatistic():
    return MultipleChoiceGoogleBarChartStatistic
