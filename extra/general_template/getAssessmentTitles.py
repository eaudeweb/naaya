#the_template = container.getSite()['tools']['general_template']['general-template']
#the_library = container.getSite()['tools']['virtual_library']['bibliography-details-each-assessment']
the_template = context
the_library = container.aq_parent.aq_parent['virtual_library']['bibliography-details-each-assessment']

def get_all_values(answer, widget_id):
    ret = []

    value = answer.get(widget_id, default=None)
    if not isinstance(value, basestring):
        for lang, lang_value in value.items():
            if lang_value:
                ret.append(lang_value)
    else:
        ret.append(value)

    return ret

posible_answers = []
the_user = container.REQUEST.AUTHENTICATED_USER.getUserName()
answered = []
for template_answer in the_template.objectValues('Naaya Survey Answer'):
    if template_answer.respondent != the_user:
        continue

    answered.append(template_answer.get('w_q1-name-assessment-report'))

lang = the_library.gl_get_selected_language()
for library_answer in the_library.objectValues('Naaya Survey Answer'):
    if library_answer.is_draft():
        continue

    values = get_all_values(library_answer, 'w_assessment-name')
    values = [value for value in values if value]
    answered_values = [value for value in values if value in answered]
    if answered_values:
        continue

    value = library_answer.get('w_assessment-name', lang=lang)
    if not value:
        value = values[0]

    posible_answers.append(value)

posible_answers.sort()
return posible_answers
