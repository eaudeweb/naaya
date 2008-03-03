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

from BaseMultipleChoiceStatistic import BaseMultipleChoiceStatistic
import pygooglechart

class MultipleChoicePieChartStatistic(BaseMultipleChoiceStatistic):
    """Piechart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoicePieChartStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Pie Chart Statistic"
    meta_label = "Multiple Choice Pie Chart Statistic"
    meta_description = """Pie Chart for every choice"""
    meta_sortorder = 220
    icon_filename = 'statistics/www/multiplechoice_piechart_statistic.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        chart = pygooglechart.PieChart3D(600, 170)
        # data
        data = [i[1] for i in per_choice]
        data.append(unanswered[1])
        chart.add_data(data)
        # legend
        legend = list(self.question.choices)
        legend.append(self.getPortalTranslations().translate('', 'Not answered'))
        chart.set_pie_labels(legend)

        return self.page(question=self.question,
                         chart_url=chart.get_url())

    page = PageTemplateFile("zpt/multiplechoice_piechart_statistics.zpt", globals())

InitializeClass(MultipleChoicePieChartStatistic)

def getStatistic():
    return MultipleChoicePieChartStatistic
