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

from Statistic import manage_addStatistic
from BaseMatrixStatistics import BaseMatrixStatistics

class MatrixCssBarChartStatistics(BaseMatrixStatistics):
    """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MatrixCssBarChartStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Matrix CSS Bar Chart Statistics"
    meta_label = "Matrix CSS Bar Chart Statistics"
    meta_sortorder = 311
    meta_description = """Table with the count and percent of answered and unanswered questions,
        diveded per choice. It should be used for matrix questions."""
    icon_filename = "statistics/www/matrix_css_barchart_statistics.gif"

    security.declarePublic('getColors')
    def getPallete(self, numcolors):
        """Get a pallete of numcolors colors.

            The colors are a list of hexadecimal codes, e.g. '#f0b0d0'.
        """
        h, s, v = 0.01, 0.55, 0.95
        step = float(1 - h) / numcolors
        colors = []
        for i in range(numcolors):
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = "%02x%02x%02x" % tuple([int(x*255) for x in h, s, v])
            colors.append(color)
            h += step
        return colors

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, unanswered, per_row_and_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         unanswered=unanswered,
                         per_row_and_choice=per_row_and_choice,
                         colors=self.getPallete(len(self.question.choices) + 1))

    page = PageTemplateFile("zpt/matrix_css_barchart_statistics.zpt", globals())

InitializeClass(MatrixCssBarChartStatistics)

def getStatistic():
    return MatrixCssBarChartStatistics
