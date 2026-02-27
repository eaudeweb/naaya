has_url = bool(datamodel['w_assessment-url'] != "")
if datamodel['w_assessment-upload'] is None:
    if not has_url and datamodel['w_paper-only'] is None:
        errors.append("Please specify a URL, upload a file or specify if the assessment was published on paper only.")

# `0` means "yes":
if datamodel['w_other-criteria'] == 0:
    if datamodel['w_main-criterion'] == "":
        errors.append("Value required for \"If yes, specify the main criterion\"")

for name in [
        'w_green-economy-topics',
        'w_resource-efficiency-topics',
        'w_water-resources-topics',
        'w_water-resource-management-topics']:
    if not datamodel[name]:
        continue
    values = dict( (k, 1) for k in datamodel[name] ).keys()
    values.sort()
    datamodel[name] = values

#themes = {0: ('green',), 1: ('water',), 2: ('green', 'water')}.get(datamodel['w_theme'], ())
#if 'green' in themes:
#    if not datamodel['w_green-economy-topics'] and not datamodel['w_resource-efficiency-topics']:
#        errors.append("Value required for \"Green economy\" or \"Resource efficiency\" topics")
#if 'water' in themes:
#    if not datamodel['w_water-resources-topics'] and not datamodel['w_water-resource-management-topics']:
#        errors.append("Value required for \"Water resources\" or \"Water resource management\" topics")

themes = []
theme_mapping = [
                (0, 'w_green-economy-topics', 'Green economy'),
                (1, 'w_water-resources-topics', 'Water resources'),
                (2, 'w_water-resource-management-topics', 'Water resource management'),
                (3, 'w_resource-efficiency-topics', 'Resource efficiency')
                ]
if datamodel['w_theme']:
    themes = datamodel['w_theme']   
for theme in theme_mapping:
    if theme[0] in themes and not datamodel[theme[1]]:
        errors.append('Value required for the "%s" topic' % theme[2])

if not context.rstk.is_valid_email(datamodel['w_submitter-email']):
    errors.append("Please enter a valid e-mail address")
