#answers = []
#the_survey = getattr(container.getSite().tools.virtual_library, 'bibliography-details-each-assessment')
#for x in the_survey.objectValues('Naaya Survey Answer'):
#  answers.append(getattr(x, 'w_assessment-name'))
#return answers

answers = []
the_user = container.REQUEST.AUTHENTICATED_USER.getUserName()
the_template = getattr(container.getSite().tools.general_template, 'general-template')
template_answers = []
for template_answer in the_template.objectValues('Naaya Survey Answer'):
    if getattr(template_answer, 'respondent') == the_user:
        template_answers.append(getattr(template_answer, 'w_q1-name-assessment-report'))
the_library = getattr(container.getSite().tools.virtual_library, 'bibliography-details-each-assessment')
for x in the_library.objectValues('Naaya Survey Answer'):
    if getattr(x, 'w_assessment-name') not in template_answers:
        answers.append(getattr(x, 'w_assessment-name'))
answers.sort()
return answers
