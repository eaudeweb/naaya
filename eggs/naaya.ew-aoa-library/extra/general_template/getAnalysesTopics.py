topics = []
the_survey = getattr(container.getSite().tools.virtual_library, 'bibliography-details-each-assessment')
for x in the_survey.objectValues('Naaya Survey Answer'):
  if getattr(x, 'w_assessment-name') == unicode(assessment, 'utf8'):
    topics = {
            'w_green-economy-topics': getattr(x, 'w_green-economy-topics'),
            'w_water-resources-topics': getattr(x, 'w_water-resources-topics'),
            'w_water-resource-management-topics': getattr(x, 'w_water-resource-management-topics'),
            'w_resource-efficiency-topics': getattr(x, 'w_resource-efficiency-topics')
            }
topics_json = container.rstk.json_dumps(topics)
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
return topics_json
