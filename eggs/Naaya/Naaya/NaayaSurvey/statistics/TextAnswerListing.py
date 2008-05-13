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
# Batranu David, Eau de Web

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaWidgets.widgets.StringWidget import StringWidget
from Products.NaayaWidgets.widgets.TextAreaWidget import TextAreaWidget

from BaseStatistic import BaseStatistic, manage_addStatistic

class TextAnswerListing(BaseStatistic):
    """Table with the count and percent of answered and unanswered questions.
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(TextAnswerListing, *args, **kw), )

    meta_type = "Naaya Survey - Text Answer Listing"
    meta_label = "Text Answer Listing"
    meta_description = """Listing with answers posted in 'Paragraph text' and 'Single line text'"""
    meta_sortorder = 100
    icon_filename = 'statistics/www/simple_tabular_statistic.gif'

    def __init__(self, id, question, lang=None, **kwargs):
        if not (isinstance(question, StringWidget) or isinstance(question, TextAreaWidget)):
            raise TypeError('Unsupported question type')
        BaseStatistic.__init__(self, id, question, lang=lang, **kwargs)

    def calculate(self, question, answers):
        """ """
        ret_data = {}
        for answer in answers:
            ret_data[answer.id] = {'respondent': answer['respondent'], 
                                   'date': self.utShowDateTime(answer['modification_time']), 
                                   'answer': answer[question.id],
                                   'answer_url': answer.absolute_url(),
                               }
        return ret_data

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        
        return self.page(data=self.calculate(self.question, answers), question=self.question)

    page = PageTemplateFile("zpt/text_answer_listing.zpt", globals())

InitializeClass(TextAnswerListing)

def getStatistic():
    return TextAnswerListing
