# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistics import BaseMultipleChoiceStatistics
import pygooglechart

class MultipleChoicePieChartStatistics(BaseMultipleChoiceStatistics):
    """Piechart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoicePieChartStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Pie Chart Statistics"
    meta_label = "Multiple Choice Pie Chart Statistics"
    meta_description = """Pie Chart for every choice"""
    meta_sortorder = 220
    icon_filename = 'statistics/www/multiplechoice_piechart_statistics.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        chart = pygooglechart.PieChart3D(600, 170)
        data = [i[1] for i in per_choice]
        data.append(unanswered[1])
        chart.add_data(data)
        legend = list(self.question.choices)
        legend.append(self.getPortalTranslations().translate('', 'Not answered'))
        chart.set_pie_labels(legend)
        # chart.set_colours(['303020', '3030f0'])
        return self.page(question=self.question,
                         chart_url=chart.get_url())

    page = PageTemplateFile("zpt/multiplechoice_piechart_statistics.zpt", globals())

InitializeClass(MultipleChoicePieChartStatistics)

def getStatistic():
    return MultipleChoicePieChartStatistics
