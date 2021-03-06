has_url = bool(datamodel['w_assessment-url'] != "")
if datamodel['w_assessment-upload'] is None:
    if not has_url:
        errors.append("Please specify a URL or upload a file.")

# `0` means "yes":
if datamodel['w_other-criteria'] == 0:
    if datamodel['w_main-criterion'] == "":
        errors.append("Value required for \"If yes, specify the main criterion\"")


themes = {0: ('green',), 1: ('water',), 2: ('green', 'water')}.get(datamodel['w_theme'], ())
if 'green' in themes:
    if not datamodel['w_green-economy-topics'] and not datamodel['w_resource-efficiency-topics']:
        errors.append("Value required for \"Green economy\" or \"Resource efficiency\" topics")
if 'water' in themes:
    if not datamodel['w_water-resources-topics'] and not datamodel['w_water-resource-management-topics']:
        errors.append("Value required for \"Water resources\" or \"Water resource management\" topics")

if not context.rstk.is_valid_email(datamodel['w_submitter-email']):
    errors.append("Please enter a valid e-mail address")
