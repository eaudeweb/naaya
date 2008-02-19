# Python imports
import colorsys

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistics import BaseMultipleChoiceStatistics
import pygooglechart

class MultipleChoiceCssBarChartStatistics(BaseMultipleChoiceStatistics):
    """Barchart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceCssBarChartStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice CSS Bar Chart Statistics"
    meta_label = "Multiple Choice CSS Bar Chart Statistics"
    meta_description = """Bar chart for every choice"""
    meta_sortorder = 211

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

InitializeClass(MultipleChoiceCssBarChartStatistics)

def getStatistic():
    return MultipleChoiceCssBarChartStatistics
