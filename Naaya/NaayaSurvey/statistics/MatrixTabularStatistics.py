# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Statistic import manage_addStatistic
from BaseMatrixStatistics import BaseMatrixStatistics

class MatrixTabularStatistics(BaseMatrixStatistics):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MatrixTabularStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Matrix Tabular Statistics"
    meta_label = "Matrix Tabular Statistics"
    meta_sortorder = 300
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions."""
    icon_filename = 'statistics/www/matrix_tabular_statistics.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered,
                         per_row_and_choice=per_row_and_choice)

    page = PageTemplateFile("zpt/matrix_tabular_statistics.zpt", globals())

InitializeClass(MatrixTabularStatistics)

def getStatistic():
    return MatrixTabularStatistics
