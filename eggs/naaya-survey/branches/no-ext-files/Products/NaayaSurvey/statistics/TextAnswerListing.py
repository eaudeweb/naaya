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

    def calculate(self, answers):
        """ """
        return self.utSortObjsListByAttr(answers, 'modification_time')

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        
        return self.page(data=self.calculate(answers), question=self.question)

    page = PageTemplateFile("zpt/text_answer_listing.zpt", globals())

    security.declarePrivate('add_to_excel')
    def add_to_excel(self, state):
        """ adds content to the excel file based on the specific statistic type """
        import xlwt
        answers = state['answers']
        ws = state['ws']
        current_row = state['current_row']
        translator = self.getSite().getPortalTranslations()
        data=self.calculate(answers)
        question=self.question

        #define Excel styles
        header_style = xlwt.easyxf('font: bold on; align: vert centre')
        normal_style = xlwt.easyxf('align: vert centre')
        hyper_style = xlwt.easyxf('align: vert centre; font: underline single, color-index blue')

        #write cell elements similarly to the zpt-->html output
        ws.write(current_row, 1, self.question.title, header_style)
        current_row += 1
        ws.write(current_row, 1, translator('User'), header_style)
        ws.write(current_row, 2, translator('Date'), header_style)
        ws.write(current_row, 3, translator('Answer'), header_style)
        current_row += 1

        for answer in data:
            if self.checkPermissionPublishObjects():
                answer_url = answer.absolute_url()
                respondent = answer.get_respondent_name()
                ws.write(current_row, 1, xlwt.Formula('HYPERLINK' + '("%s"; "%s")'
                    % (answer_url, respondent)), hyper_style)
            ws.write(current_row, 2,
                self.utShowDateTime(answer.modification_time), normal_style)

            response = answer.get(question.id, '', lang=self.gl_get_selected_language())
            # try to get any response if multilingual
            if not response:
                all_responses = answer.get(question.id, '')
                if isinstance(all_responses, dict):
                    all_responses = filter(None, all_responses.values())
                    if len(all_responses) > 0:
                        response = all_responses[0]

            ws.write(current_row, 3,
                self.utLinkifyURLs(response) or 'No response.', normal_style)
            current_row += 1

        state['current_row'] = current_row + 1

InitializeClass(TextAnswerListing)

def getStatistic():
    return TextAnswerListing
