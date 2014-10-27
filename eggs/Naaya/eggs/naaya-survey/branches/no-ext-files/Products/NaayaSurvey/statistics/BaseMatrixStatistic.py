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
from Products.NaayaWidgets.widgets.RadioMatrixWidget import RadioMatrixWidget
from Products.NaayaWidgets.widgets.CheckboxMatrixWidget import CheckboxMatrixWidget

from BaseStatistic import BaseStatistic

class BaseMatrixStatistic(BaseStatistic):
    """Base class for calculating statistics for matrix questions"""

    def __init__(self, id, question, lang=None, **kwargs):
        if not isinstance(question, (RadioMatrixWidget, CheckboxMatrixWidget)):
            raise TypeError('Unsupported question type')
        BaseStatistic.__init__(self, id, question, lang=lang, **kwargs)

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered, per_choice)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        per_row_and_choice_count = [[0 for c in question.choices] for r in question.rows]
        unanswered_count = [0 for r in question.rows]
        for answer in answers:
            total += 1
            answer = answer.get(w_id)
            if answer is None:
                for i in range(len(unanswered_count)):
                    unanswered_count[i] += 1
                continue
            for r, per_row_choices in enumerate(answer):
                if isinstance(per_row_choices, int):
                    # 1 answer question
                    per_row_and_choice_count[r][per_row_choices] += 1
                elif per_row_choices:
                    # multiple answers question
                    for i in per_row_choices:
                        per_row_and_choice_count[r][i] += 1
                else:
                    unanswered_count[r] += 1

        if total:
            unanswered_percent = [100.0 * x / total for x in unanswered_count]
            per_row_and_choice_percent = \
                    [[100.0 * i / total for i in per_choice_count] \
                            for per_choice_count in per_row_and_choice_count]
        else:
            unanswered_percent = [0.0 for x in unanswered_count]
            per_row_and_choice_percent = \
                    [[0 for i in per_choice_count] \
                            for per_choice_count in per_row_and_choice_count]

        per_row_and_choice = []
        for x, y in zip(per_row_and_choice_count, per_row_and_choice_percent):
            per_row_and_choice.append(zip(x, y))

        return (total,
                zip(unanswered_count, unanswered_percent),
                per_row_and_choice)
