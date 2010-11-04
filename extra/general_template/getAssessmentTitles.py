#the_template = container.getSite()['tools']['general_template']['general-template']
#the_library = container.getSite()['tools']['virtual_library']['bibliography-details-each-assessment']
the_template = context
the_library = container.aq_parent.aq_parent['virtual_library']['bibliography-details-each-assessment']

answers = []
the_user = container.REQUEST.AUTHENTICATED_USER.getUserName()
template_answers = []
for template_answer in the_template.objectValues('Naaya Survey Answer'):
    if getattr(template_answer, 'respondent') == the_user:
        template_answers.append(getattr(template_answer, 'w_q1-name-assessment-report'))

for x in the_library.objectValues('Naaya Survey Answer'):
    if getattr(x, 'w_assessment-name') not in template_answers:
        answers.append(getattr(x, 'w_assessment-name'))
answers.sort()
return answers
