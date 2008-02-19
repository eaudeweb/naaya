from Statistic import Statistic

class BaseMatrixStatistics(Statistic):
    """Base class for calculating statistics for matrix questions"""

    def calculate(self, question, answers):
        """ -> (total, answered, unanswered, per_choice)"""
        w_id = question.getWidgetId()
        total = answered_count = 0
        per_row_and_choice_count = [[0 for c in question.choices] for r in question.rows]
        for answer in answers:
            total += 1
            answer = getattr(answer, w_id, None)
            if answer is None:
                continue
            incomplete_answer = False
            for r, per_row_choices in enumerate(answer):
                if isinstance(per_row_choices, int):
                    # 1 answer question
                    per_row_and_choice_count[r][per_row_choices] += 1
                elif per_row_choices:
                    # multiple answers question
                    for i in per_row_choices:
                        per_row_and_choice_count[r][i] += 1
                else:
                    incomplete_answer = True
            if not incomplete_answer:
                answered_count += 1

        unanswered_count = total - answered_count
        if total:
            answered_percent = 100.0 * answered_count / total
            unanswered_percent = 100.0 * unanswered_count / total
            per_row_and_choice_percent = \
                    [[100.0 * i / total for i in per_choice_count] \
                            for per_choice_count in per_row_and_choice_count]
        else:
            answered_percent = unanswered_percent = 0
            per_row_and_choice_percent = \
                    [[0 for i in per_choice_count] \
                            for per_choice_count in per_row_and_choice_count]

        per_row_and_choice = []
        for x, y in zip(per_row_and_choice_count, per_row_and_choice_percent):
            per_row_and_choice.append(zip(x, y))

        return (total,
                (answered_count, answered_percent),
                (unanswered_count, unanswered_percent),
                per_row_and_choice)
