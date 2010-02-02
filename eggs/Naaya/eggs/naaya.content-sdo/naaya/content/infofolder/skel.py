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

sdo_type_of_initiative = {
          'list_id': 'sdo_type_of_initiative',
          'list_title': 'Type of initiative',
          'list_items':  [
                    'Information Dissemination', 'Support Centre', 'Network - Club',
                    'Supply Chain Initiative', 'Funding Programmes', 'Other'
                    ]
}
sdo_nature_of_initiative = {
          'list_id': 'sdo_nature_of_initiative',
          'list_title': 'Nature of initiative',
          'list_items':  [
                    'Active - Hands-On', 'Passive - Hands-Off', 'Long Term - Years',
                    'Medium Term - Months', 'Short Term - One-Off Days'
                    ]
}
sdo_topic_coverage = {
          'list_id': 'sdo_topic_coverage',
          'list_title': 'Topic Coverage',
          'list_items':  [
                    'Eco-Efficiency', 'Eco-Design', 'Working Environment',
                    'Sustainable Manufacturing', 'Other'
                    ]
}
sdo_services = {
          'list_id': 'sdo_services',
          'list_title': 'Services',
          'list_items':  [
                    'Coordination - Facilitation', 'Info - advice on paper', 'Electronic information',
                    'Workshops - Seminars', 'Consultancy Services', 'Other'
                    ]
}
sdo_geographic_scope = {
          'list_id': 'sdo_geographic_scope',
          'list_title': 'Geographic Scope',
          'list_items':  ['International', 'National', 'Regional', 'Local']
}

sdo_network_type = {
          'list_id': 'sdo_network_type',
          'list_title': 'Network type',
          'list_items':  ['Formal', 'Informal']
}
sdo_scope = {
          'list_id': 'sdo_scope',
          'list_title': 'Scope',
          'list_items':  ['Holistic', 'Broad', 'Specialist']
}
sdo_audience = {
          'list_id': 'sdo_audience',
          'list_title': 'Audience',
          'list_items':  ['Business', 'Community', 'Policy', 'Research']
}
sdo_status = {
          'list_id': 'sdo_status',
          'list_title': 'Status',
          'list_items':  ['Pioneer', 'Progressive', 'Supportive']
}

sdo_type_of_event = {
          'list_id': 'sdo_type_of_event',
          'list_title': 'Type of event',
          'list_items':  [
                    'Conference', 'Seminar', 'Forum', 'Round table', 'Summit',
                    'Symposium', 'Consultation', 'Workshop', 'Meeting',
                    'Trade show', 'Product/Service launch', 'Other'
                    ]
}

sdo_tool_type = {
          'list_id': 'sdo_tool_type',
          'list_title': 'Tool type',
          'list_items':  [
                    'Dissemination of information', 'Ecodesign', 'Environmental management',
                    'Life Cycle Analysis', 'Policy instrument', 'Pollution prevention', 'Other'
                    ]
}
sdo_tool_sort = {
          'list_id': 'sdo_tool_sort',
          'list_title': 'Tool sort',
          'list_items':  [
                    'Case study', 'Software', 'Checklist', 'Guide - manual', 'Journal-Magazine',
                    'Labelling - General info', 'Labelling I - Third Party',
                    'Labelling II - Self Declared', 'Labelling III - LCA based',
                    'Labelling - Other', 'Study - report', 'Web - online', 'Other'
                    ]
}

sdo_training_type = {
          'list_id': 'sdo_training_type',
          'list_title': 'Training type',
          'list_items':  [
                    'Distance learning', 'Computer Based Training', 'Fellowship',
                    'Postgraduate', 'Journal-Magazine', 'Professional training', 'Other'
                    ]
}

FOLDER_CATEGORIES = [
        sdo_type_of_initiative, sdo_nature_of_initiative,
        sdo_topic_coverage, sdo_services, sdo_geographic_scope,
        sdo_network_type, sdo_scope, sdo_audience, sdo_status,
        sdo_type_of_event,
        sdo_tool_type, sdo_tool_sort,
        sdo_training_type
        ]

countries = {
          'list_id': 'countries',
          'list_title': 'Country',
}
sdo_ep_frequency = {
          'list_id': 'sdo_ep_frequency',
          'list_title': 'Frequency',
          'list_items':  ['Contact provider', 'Once', 'Monthly', 'Biannual', 'Yearly',
                    'Several times a year', 'Continuous', 'Upon request']
}
sdo_ep_duration = {
          'list_id': 'sdo_ep_duration',
          'list_title': 'Duration',
          'list_items': [
                'Own schedule', 'Contact provider', 'One day', 'Several days', 'One week',
                'Several weeks', 'One month', 'Several months', 'Half a year',
                'Three quarters of a year', 'One year', 'One and a half years', 'Two years',
                'Three years', 'Four years']
}

EXTRA_PROPERTIES = [countries, sdo_ep_frequency, sdo_ep_duration]

EXTRA_FIELDS = [
                    ['subtitle', 'Subtitle', 'String'],
                    ['start_date', 'Start date', 'Date'],
                    ['end_date', 'End date', 'Date'],
                    ['location', 'Location', 'String'],
                    ['training_city', 'Training city', 'String'],
                   ]