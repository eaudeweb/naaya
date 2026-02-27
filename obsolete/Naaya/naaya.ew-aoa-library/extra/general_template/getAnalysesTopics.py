#the_survey = container.getSite()['tools']['virtual_library']['bibliography-details-each-assessment']
the_survey = container.aq_parent.aq_parent['virtual_library']['bibliography-details-each-assessment']

topics = {
        'w_green-economy-topics': [],
        'w_water-resources-topics': [],
        'w_water-resource-management-topics': [],
        'w_resource-efficiency-topics': []
        }
unicode_assessment = unicode(assessment, 'utf8')

for x in the_survey.objectValues('Naaya Survey Answer'):
    value = x.get('w_assessment-name')
    if isinstance(value, basestring):
        values = [value]
    elif value is not None:
        values = value.values()
    else:
        values = []

    if unicode_assessment in values:
        topics = {
                'w_green-economy-topics': getattr(x, 'w_green-economy-topics'),
                'w_water-resources-topics': getattr(x, 'w_water-resources-topics'),
                'w_water-resource-management-topics': getattr(x, 'w_water-resource-management-topics'),
                'w_resource-efficiency-topics': getattr(x, 'w_resource-efficiency-topics')
                }
topics_json = container.rstk.json_dumps(topics)
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
return topics_json
