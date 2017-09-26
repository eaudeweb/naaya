#the_template = container.getSite()['tools']['general_template']['general-template']
#the_library = container.getSite()['tools']['virtual_library']['bibliography-details-each-assessment']
the_template = context
the_library = container.aq_parent.aq_parent['virtual_library']['bibliography-details-each-assessment']

def force_to_unicode(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            return s.decode('latin-1')
    else:
        raise ValueError('expected `str` or `unicode`')

def get_all_values_with_lang(answer, widget_id):
    ret = {}

    value = answer.get(widget_id, default=None)
    if not isinstance(value, basestring):
        if hasattr(value, 'items'):
            for lang, lang_value in value.items():
                lang_value = lang_value.strip()
                if lang_value:
                    ret[lang] = force_to_unicode(lang_value)
    elif value:
        ret['en'] = force_to_unicode(value)

    return ret

possible_answers = {}
answered = []
the_user = container.REQUEST.AUTHENTICATED_USER.getUserName()

for template_answer in the_template.objectValues('Naaya Survey Answer'):
    if template_answer.respondent == the_user:
        vlid = getattr(template_answer, 'w_vlid')
        if vlid:
            answered.append(vlid)

lang = the_library.gl_get_selected_language()
for library_answer in the_library.objectValues('Naaya Survey Answer'):
    if library_answer.is_draft():
        continue
    if library_answer.getId() in answered:
        continue
    title_values = get_all_values_with_lang(library_answer, 'w_assessment-name')
    possible_answers[library_answer.getId()] = title_values

return possible_answers
