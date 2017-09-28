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

# Naaya imports
from Products.NaayaWidgets.widgets.ComboboxWidget import ComboboxWidget
from Products.NaayaWidgets.widgets.RadioWidget import RadioWidget
from Products.NaayaWidgets.widgets.CheckboxesWidget import CheckboxesWidget

from BaseStatistic import BaseStatistic

class BaseMultipleChoiceStatistic(BaseStatistic):
    """Base class for calculating statistics for multiple choice questions"""

    def __init__(self, id, question, lang=None, **kwargs):
        if not isinstance(question, (ComboboxWidget, RadioWidget, CheckboxesWidget)):
            raise TypeError('Unsupported question type')
        BaseStatistic.__init__(self, id, question, lang=lang, **kwargs)

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered, per_choice)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        per_choice_count = [0 for i in range(len(question.getChoices()))]
        for answer in answers:
            total += 1
            choice = answer.get(w_id)
            if choice is None:
                continue
            if isinstance(question, RadioWidget) and question.add_extra_choice:
                choice = choice[0]
            if isinstance(choice, int):
                # 1 answer question
                answered_count += 1
                per_choice_count[choice] += 1
            else:
                # multiple answers question
                if choice:
                    answered_count += 1
                for i in choice:
                    try:
                        per_choice_count[i] += 1
                    except IndexError:
                        self.setSessionErrorsTrans(
                            'Error at question "%s" there are more user '
                            'selected answers than available choices (possibly '
                            'because in other languages there are more choices '
                            'for this question). Reports cannot be generated '
                            'until there are enough choices for this question '
                            'to cover existing answers.'
                            % question.title)
                        self.REQUEST.RESPONSE.redirect(self.REQUEST.HTTP_REFERER)

        unanswered_count = total - answered_count
        if total:
            answered_percent = 100.0 * answered_count / total
            unanswered_percent = 100.0 * unanswered_count / total
            per_choice_percent = [100.0 * i / total for i in per_choice_count]
        else:
            answered_percent = unanswered_percent = 0
            per_choice_percent = [0 for i in per_choice_count]
        return (total,
                (answered_count, answered_percent),
                (unanswered_count, unanswered_percent),
                zip(per_choice_count, per_choice_percent))
