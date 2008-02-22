# Naaya imports
from Products.NaayaWidgets.widgets.RadioMatrixWidget import RadioMatrixWidget
from Products.NaayaWidgets.widgets.CheckboxMatrixWidget import CheckboxMatrixWidget

from Statistic import Statistic

class BaseMatrixStatistics(Statistic):
    """Base class for calculating statistics for matrix questions"""

    def __init__(self, id, question, lang=None, **kwargs):
        if not isinstance(question, (RadioMatrixWidget, CheckboxMatrixWidget)):
            raise TypeError('Unsupported question type')
        Statistic.__init__(self, id, question, lang=None, **kwargs)

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered, per_choice)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        per_row_and_choice_count = [[0 for c in question.choices] for r in question.rows]
        unanswered_count = [0 for r in question.rows]
        for answer in answers:
            total += 1
            answer = getattr(answer, w_id, None)
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
