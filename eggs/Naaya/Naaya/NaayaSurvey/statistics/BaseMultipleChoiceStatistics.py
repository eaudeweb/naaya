# Naaya imports
from Products.NaayaWidgets.widgets.ComboboxWidget import ComboboxWidget
from Products.NaayaWidgets.widgets.RadioWidget import RadioWidget
from Products.NaayaWidgets.widgets.CheckboxesWidget import CheckboxesWidget

from Statistic import Statistic

class BaseMultipleChoiceStatistics(Statistic):
    """Base class for calculating statistics for multiple choice questions"""

    def __init__(self, id, question, lang=None, **kwargs):
        if not isinstance(question, (ComboboxWidget, RadioWidget, CheckboxesWidget)):
            raise TypeError('Unsupported question type')
        Statistics.__init__(self, id, question, lang=None, **kwargs)

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered, per_choice)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        per_choice_count = [0 for i in range(len(question.choices))]
        for answer in answers:
            total += 1
            choice = getattr(answer, w_id, None)
            if choice is None:
                continue
            if isinstance(choice, int):
                # 1 answer question
                answered_count += 1
                per_choice_count[choice] += 1
            else:
                # multiple answers question
                if choice:
                    answered_count += 1
                for i in choice:
                    per_choice_count[i] += 1

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
