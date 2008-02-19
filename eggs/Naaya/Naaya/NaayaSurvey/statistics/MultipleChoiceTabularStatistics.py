# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Statistic import manage_addStatistic
from BaseMultipleChoiceStatistics import BaseMultipleChoiceStatistics

class MultipleChoiceTabularStatistics(BaseMultipleChoiceStatistics):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for multiple choice questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceTabularStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice Tabular Statistics"
    meta_label = "Multiple Choice Tabular Statistics"
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for multiple choice questions."""
    meta_sortorder = 200
    icon_filename = 'statistics/www/multiplechoice_tabular_statistics.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered,
                         per_choice=per_choice)

    page = PageTemplateFile("zpt/multiplechoice_tabular_statistics.zpt", globals())

InitializeClass(MultipleChoiceTabularStatistics)

def getStatistic():
    return MultipleChoiceTabularStatistics
