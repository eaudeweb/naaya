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

from BaseStatistic import manage_addStatistic
from BaseMatrixStatistic import BaseMatrixStatistic

class MatrixTabularStatistic(BaseMatrixStatistic):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MatrixTabularStatistic, *args, **kw), )

    meta_type = "Naaya Survey - Matrix Tabular Statistic"
    meta_label = "Matrix Tabular Statistic"
    meta_sortorder = 300
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions."""
    icon_filename = 'statistics/www/matrix_tabular_statistic.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         unanswered=unanswered,
                         per_row_and_choice=per_row_and_choice)

    page = PageTemplateFile("zpt/matrix_tabular_statistics.zpt", globals())

InitializeClass(MatrixTabularStatistic)

def getStatistic():
    return MatrixTabularStatistic
