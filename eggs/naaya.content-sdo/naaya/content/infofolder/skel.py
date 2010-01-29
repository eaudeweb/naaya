# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Valentin Dumitru, Eau de Web

enterprises_type_of_initiative = {
          'list_id': 'enterprises_type_of_initiative',
          'list_title': 'Type of initiative',
          'list_items':  [
                    'Information Dissemination', 'Support Centre', 'Network - Club',
                    'Supply Chain Initiative', 'Funding Programmes', 'Other'
                    ]
}
enterprises_nature_of_initiative = {
          'list_id': 'enterprises_nature_of_initiative',
          'list_title': 'Nature of initiative',
          'list_items':  [
                    'Active - Hands-On', 'Passive - Hands-Off', 'Long Term - Years',
                    'Medium Term - Months', 'Short Term - One-Off Days'
                    ]
}
enterprises_topic_coverage = {
          'list_id': 'enterprises_topic_coverage',
          'list_title': 'Topic Coverage',
          'list_items':  [
                    'Eco-Efficiency', 'Eco-Design', 'Working Environment',
                    'Sustainable Manufacturing', 'Other'
                    ]
}
enterprises_services = {
          'list_id': 'enterprises_services',
          'list_title': 'Services',
          'list_items':  [
                    'Coordination - Facilitation', 'Info - advice on paper', 'Electronic information',
                    'Workshops - Seminars', 'Consultancy Services', 'Other'
                    ]
}
enterprises_geographic_scope = {
          'list_id': 'enterprises_geographic_scope',
          'list_title': 'Geographic Scope',
          'list_items':  ['International', 'National', 'Regional', 'Local']
}

networks_network_type = {
          'list_id': 'networks_network_type',
          'list_title': 'Network type',
          'list_items':  ['Formal', 'Informal']
}
networks_scope = {
          'list_id': 'networks_scope',
          'list_title': 'Scope',
          'list_items':  ['Holistic', 'Broad', 'Specialist']
}
networks_audience = {
          'list_id': 'networks_audience',
          'list_title': 'Audience',
          'list_items':  ['Business', 'Community', 'Policy', 'Research']
}
networks_status = {
          'list_id': 'networks_status',
          'list_title': 'Status',
          'list_items':  ['Pioneer', 'Progressive', 'Supportive']
}

events_type_of_event = {
          'list_id': 'events_type_of_event',
          'list_title': 'Type of event',
          'list_items':  [
                    'Conference', 'Seminar', 'Forum', 'Round table', 'Summit',
                    'Symposium', 'Consultation', 'Workshop', 'Meeting',
                    'Trade show', 'Product/Service launch', 'Other'
                    ]
}

tools_tool_type = {
          'list_id': 'tools_tool_type',
          'list_title': 'Tool type',
          'list_items':  [
                    'Dissemination of information', 'Ecodesign', 'Environmental management',
                    'Life Cycle Analysis', 'Policy instrument', 'Pollution prevention', 'Other'
                    ]
}
tools_tool_sort = {
          'list_id': 'tools_tool_sort',
          'list_title': 'Tool sort',
          'list_items':  [
                    'Case study', 'Software', 'Checklist', 'Guide - manual', 'Journal-Magazine',
                    'Labelling - General info', 'Labelling I - Third Party',
                    'Labelling II - Self Declared', 'Labelling III - LCA based',
                    'Labelling - Other', 'Study - report', 'Web - online', 'Other'
                    ]
}

training_training_type = {
          'list_id': 'training_training_type',
          'list_title': 'Training type',
          'list_items':  [
                    'Distance learning', 'Computer Based Training', 'Fellowship',
                    'Postgraduate', 'Journal-Magazine', 'Professional training', 'Other'
                    ]
}

URL_CATEGORIES = [
        enterprises_type_of_initiative, enterprises_nature_of_initiative,
        enterprises_topic_coverage, enterprises_services, enterprises_geographic_scope,
        networks_network_type, networks_scope, networks_audience, networks_status,
        events_type_of_event,
        tools_tool_type, tools_tool_sort,
        training_training_type
        ]

countries = {
          'list_id': 'countries',
          'list_title': 'Countries',
}
extra_properties_frequency = {
          'list_id': 'extra_properties_frequency',
          'list_title': 'Frequency',
          'list_items':  ['Contact provider', 'Once', 'Monthly', 'Biannual', 'Yearly',
                    'Several times a year', 'Continuous', 'Upon request']
}
extra_properties_duration = {
          'list_id': 'extra_properties_duration',
          'list_title': 'Duration',
          'list_items': [
                'Own schedule', 'Contact provider', 'One day', 'Several days', 'One week',
                'Several weeks', 'One month', 'Several months', 'Half a year',
                'Three quarters of a year', 'One year', 'One and a half years', 'Two years',
                'Three years', 'Four years']
}

EXTRA_PROPERTIES_LISTS = [countries, extra_properties_frequency, extra_properties_duration]

EXTRA_PROPERTIES = [
                    ['subtitle', 'Subtitle', 'String'],
                    ['start_date', 'Start date', 'Date'],
                    ['end_date', 'End date', 'Date'],
                    ['location', 'Location', 'String'],
                    ['training_city', 'Training city', 'String'],
                   ]