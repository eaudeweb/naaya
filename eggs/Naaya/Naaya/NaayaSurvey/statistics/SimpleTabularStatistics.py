# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Statistic import Statistic, manage_addStatistic

class SimpleTabularStatistics(Statistic):
    """Table with the count and percent of answered and unanswered questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(SimpleTabularStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Simple Tabular Statistics"
    meta_label = "Simple Tabular Statistics"
    meta_description = """Table with the count and percent of answered and unanswered questions."""
    meta_sortorder = 100
    icon_filename = 'statistics/www/simple_tabular_statistics.gif'

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        for answer in answers:
            val = getattr(answers, w_id, None)
            if val is not None:
                answered_count += 1
            total += 1

        unanswered_count = total - answered_count
        if total:
            answered_percent = 100.0 * answered_count / total
            unanswered_percent = 100.0 * unanswered_count / total
        else:
            answered_percent = unanswered_percent = 0
        return (total,
                (answered_count, answered_percent),
                (unanswered_count, unanswered_percent))

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered)

    page = PageTemplateFile("zpt/simple_tabular_statistics.zpt", globals())

InitializeClass(SimpleTabularStatistics)

def getStatistic():
    return SimpleTabularStatistics
