# Python imports
import colorsys

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistics import BaseMultipleChoiceStatistics
import pygooglechart

class MultipleChoiceGoogleBarChartStatistics(BaseMultipleChoiceStatistics):
    """Barchart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceGoogleBarChartStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Google Bar Chart Statistics"
    meta_label = "Multiple Choice Google Bar Chart Statistics"
    meta_description = """Bar chart for every choice"""
    meta_sortorder = 210

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        chart = pygooglechart.GroupedHorizontalBarChart(500, 300)
        chart.set_bar_width(5)
        data = [unanswered[0]]
        data += [i[0] for i in per_choice]
        for x in data:
            chart.add_data([x, 0]) # the 0 is an ugly hack
        legend = ['No choice']
        legend.extend(self.question.choices)
        chart.set_legend(legend)

        colors = []
        h, s, v = 0.01, 0.55, 0.95
        step = float(1 - h) / (len(self.question.choices) + 1)
        for i in range(len(self.question.choices) + 1):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = "%02x%02x%02x" % tuple([int(x*255) for x in h, s, v])
            colors.append(color)
            h += step
        chart.set_colours(colors)

        return self.page(question=self.question,
                         chart_url=chart.get_url())

    page = PageTemplateFile("zpt/multiplechoice_barchart_statistics.zpt", globals())

InitializeClass(MultipleChoiceGoogleBarChartStatistics)

def getStatistic():
    return MultipleChoiceGoogleBarChartStatistics
