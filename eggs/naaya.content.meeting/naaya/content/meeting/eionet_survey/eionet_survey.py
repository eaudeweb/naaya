EIONET_MEETINGS = ['NRC meeting', 'NRC webinar', 'NFP meeting', 'NFP webinar']
EIONET_SURVEYS = {
    'NFP meeting': {
        'id': 'eionet-survey-nfp-meeting',
        'title': 'Eionet NFP meeting evaluation survey',
        'description': ('Thank you for completing the form.'
                        'Your comments will be very useful in strengthening '
                        'EEA/Eionet cooperation. This evaluation form covers '
                        'all meetings in 2015.'),
        'questions': [
            {'meta_type': 'Naaya Label Widget',
             'title': 'Introductory Questions',
             'sortorder': 1},

            {'meta_type': 'Naaya Radio Widget',
             'title': 'I am attending the NFP/Eionet meeting as',
             'choices': ['NFP',
                         'NFP alternate or assistant',
                         'ETC',
                         'European Commission'],
             'sortorder': 2,
             'add_extra_choice': True,
             'required': False},

            {'meta_type': 'Naaya String Widget',
             'title': 'I work at',
             'tooltips': '(your host organisation and country)',
             'sortorder': 3,
             'required': True},

            {'meta_type': 'Naaya Radio Widget',
             'title': 'Number of NFP/Eionet meetings attended',
             'choices': ['This was the first meeting',
                         '2-5 meetings',
                         '6-10 meetings',
                         '10 < meetings'],
             'sortorder': 4,
             'required': True},

            {'meta_type': 'Naaya Radio Widget',
             'title': 'How much time did you spend preparing for the meeting?',
             'choices': ['0-2 hours',
                         '2-5 hours',
                         '5-10 hours',
                         '10 < hours',
                         'I did not prepare'],
             'sortorder': 5,
             'required': True},

            {'meta_type': 'Naaya Checkboxes Widget',
             'title': 'How did you prepare for the meeting?',
             'choices': ['Read the meeting documents',
                         'Prepared a presentation, poster, etc. that was '
                         'shared during the meeting',
                         'Discussed the meeting documents with my national '
                         'network (MB member, NRC, other expert)',
                         'Discussed the meeting documents with other meeting '
                         'participants',
                         'Organised a working group meeting'],
             'sortorder': 6,
             'required': True},

            {'meta_type': 'Naaya Label Widget',
             'title': 'Relevance (agenda and content)',
             'sortorder': 6},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': ' Please rank accordingly',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': [
                 'How relevant was the meeting to your daily work as NFP?',
                 'How relevant was the meeting to the overall operation of '
                 'Eionet in your country?',
                 'How well did the agenda reflect the strategic priorities of '
                 'EEA/Eionet?',
                 'How well did the agenda address EU policy issues and '
                 'processes relevant to Eionet?'
             ],
             'sortorder': 7,
             'required': True},

            {'meta_type': 'Naaya Checkboxes Widget',
             'title': 'Please select the sessions that were most relevant to '
                      'your work',
             'choices': ['Session 1: Governance issues',
                         'Session 2: Cooperation and Development',
                         'Session 3: ED outlook',
                         'Session 4: Integrated Assessments',
                         'Session 5: 2019 Key Priorities - Plenary: Part A',
                         'Session 5: 2019 Key Priorities - '
                         'Break out discussions: Part B',
                         'Session 5: 2019 Key Priorities - Plenary: Part C',
                         ],
             'sortorder': 8,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Please give examples of how you intend to use the '
                      'outcome of this meeting in your daily work as NFP',
             'sortorder': 9,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Please list key topics/issues that you would find '
                      'relevant in a future NFP/Eionet meeting',
             'sortorder': 10,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Label Widget',
             'title': 'Performance (chairing and engagement)',
             'sortorder': 11},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate the following elements of the '
                      'meeting?',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['Pre-meeting',
                      'Facilitation/interaction during break-out sessions',
                      'Poster session'],
             'sortorder': 12,
             'required': True},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate the chairing of the sessions?',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['Welcome and opening of the meeting',
                      'S1: Governance issues 	',
                      'S2: Cooperation and Development',
                      'S3: ED outlook',
                      'S4: Integrated Assessments',
                      'S5: 2019 Key Priorities - Plenary: Part A',
                      'S5: 2019 Key Priorities - Plenary: Part C',
                      ],
             'sortorder': 13,
             'required': True},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate country engagement during this '
                      'meeting, in terms of',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['General engagement of countries during plenaries',
                      'General engagement of countries during break out '
                      'discussions',
                      'Your contributions to this meeting',
                      ],
             'sortorder': 14,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Please elaborate on your ranking above',
             'sortorder': 15,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate the networking opportunities during '
                      'the meeting, in relation to',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['The Eionet team',
                      'The Country Desk Officers',
                      'Other EEA colleagues',
                      'Other members of Eionet',
                      'Members of the European Commission',
                      ],
             'sortorder': 16,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'How would you like networking opportunities to be '
                      'strengthened in future NFP meetings?',
             'sortorder': 17,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'How would you like to contribute to the success of '
                      'future NFP meetings?',
             'sortorder': 18,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Label Widget',
             'title': 'Preparations and Outcome',
             'sortorder': 19},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate the preparation of the meeting, '
                      'in terms of',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['Relevance of background documents',
                      'Timeliness of background documents',
                      'Specification of EEA expectations regarding Eionet '
                      'involvement',
                      ],
             'sortorder': 20,
             'required': True},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate the outcome of this meeting, in '
                      'terms of',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['Usefulness',
                      'Efficiency',
                      'Effectiveness',
                      ],
             'sortorder': 21,
             'required': True},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'To what extent has EEA/Eionet achieved the objectives '
                      'of this meeting?',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['S1: Governance issues',
                      'S2: Cooperation and Development',
                      'S3: ED outlook',
                      'S4: Integrated Assessments',
                      'S5: 2019 Key Priorities - Plenary: Part A',
                      'S5: 2019 Key Priorities - Break out discussions: '
                      'Part B',
                      'S5: 2019 Key Priorities - Plenary: Part C',
                      ],
             'sortorder': 22,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Please explain what could be improved in future '
                      'meetings',
             'sortorder': 23,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Label Widget',
             'title': 'Value added',
             'sortorder': 24},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'How would you like EEA/Eionet to work together to '
                      'implement the work programmes 2019-2020?',
             'sortorder': 25,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'From a national perspective, what do you see as the '
                      'future challenges for Eionet?',
             'sortorder': 26,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'How would you like to see the role of the NFP develop '
                      'in the years to come?',
             'sortorder': 27,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Which main Eionet assets/features would you like to '
                      'see in the next strategy (2020-2030)?',
             'sortorder': 28,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Which Eionet features/activities, if any, would you '
                      'consider outdated/irrelevant for the future of Eionet?',
             'sortorder': 29,
             'rows': 5,
             'required': True},

            {'meta_type': 'Naaya Label Widget',
             'title': 'Meeting organisation',
             'sortorder': 30},

            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': 'How would you rate the following support?',
             'tooltips': '5 is the top score',
             'choices': ['1', '2', '3', '4', '5', 'N/A'],
             'rows': ['EEA secretarial service',
                      'Travel arrangements provided by BCD',
                      'Social arrangements',
                      ],
             'sortorder': 31,
             'required': True},

            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Please list recommendations for improvements',
             'sortorder': 32,
             'rows': 5,
             'required': True},
        ]
    },
    'NRC meeting': {
        'id': 'eionet-survey',
        'title': 'Eionet NRC meeting evaluation survey',
        'description': ('Thank you for completing the evaluation form.'
                        'Your opinions are valuable for our efforts to '
                        'strengthen EEA/Eionet cooperation.'),
        'questions': [
            {'meta_type': 'Naaya Checkboxes Widget',
             'title': '1.1. I am',
             'choices': ['National Reference Centre', 'National Focal Point',
                         'European Topic Centre', 'Other Participant'],
             'sortorder': 1,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': '1.2. Have you attended previous Eionet workshops?',
             'choices': ['None', '1-3 times', '4-10 times',
                         'More than 10 times'],
             'sortorder': 2,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': '2.1. How did you find the workshop overall in terms '
                      'of usefulness?',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent'],
             'sortorder': 3,
             'required': False},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '2.2. Workshop agenda and objectives',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': ['2.2.1 Were the objectives of the workshop clear?',
                      '2.2.2 Was the agenda of the workshop clear?',
                      ('2.2.3 Do you think the background materials were '
                       'relevant?'),
                      '2.2.4 Was the right mix of topics covered?',
                      ('2.2.5 Were the background documents useful to you in '
                       'your daily job?'),
                      ('2.2.6 Did you share the documents or other information'
                          ' with your colleagues?'),
                      '2.2.7 Were the objectives of the workshop achieved?'],
             'sortorder': 4,
             'required': False},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '3. Workshop content and programme',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': ['3.1 Relevance of the agenda for your work',
                      ('3.2 Balance of content between European and country '
                       'level'),
                      '3.3 Facilitation / Chairing (if applicable)',
                      '3.4 Use of practical examples / case studies',
                      '3.5 Quality of presentations',
                      '3.6 Engagement with ETC partners, if applicable',
                      '3.7 Exchange of information and experiences'],
             'sortorder': 5,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': '4. Further comments on the above',
             'tooltips': ('(e.g. usefulness of specific presentations etc.)'),
             'sortorder': 6,
             'rows': 5},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '5. Organisational aspects',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': ['5.1 Travel arrangements prior to workshop',
                      '5.2 Secretariat support',
                      ('5.3 Working conditions during this workshop '
                          '(conference room facilities, equipment etc.)'),
                      '5.4 Convenience of the location'],
             'sortorder': 7,
             'required': False},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '6. Time allocation',
             'choices': ['Too short', 'Fine', 'Too long',
                         'I prefer not to answer'],
             'rows': ['6.1 Length of the Eionet workshop',
                      '6.2 Length of time allocated to discussions',
                      ('6.3 Length of time allocated to country level '
                       'experiences'),
                      '6.4 Time for networking, including social events'],
             'sortorder': 8,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('7. Please cite the 3 most valuable pieces of '
                       'information you have gained from this workshop.'),
             'sortorder': 9,
             'rows': 5},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('8.1 Ideas for further improving Eionet workshops '
                       '- Address additional topics?'),
             'choices': ['Yes', 'No', 'I prefer not to answer'],
             'sortorder': 10,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': 'If yes, please specify',
             'sortorder': 11,
             'rows': 5},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('8.2 Do you consider communication between EEA and '
                       'NRCs between workshops sufficient?'),
             'choices': ['Yes', 'No', 'I prefer not to answer'],
             'sortorder': 12,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': 'If no, please provide suggestions',
             'sortorder': 13,
             'rows': 5},
            {'meta_type': 'Naaya Checkboxes Widget',
             'title': ('8.3 Which forms of communication do you prefer '
                       'between Eionet workshops? (multiple choice)'),
             'choices': ['E-mail', 'Eionet Forum', 'Social media platforms',
                         'Webinar', 'Newsletter'],
             'sortorder': 14, 'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': 'Any additional comments',
             'tooltips': ('(e.g. unintended benefits, the most positive '
                          'or negative aspects)'),
             'sortorder': 15,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': 'Thank you!',
             'sortorder': 16}
        ]
    },
    'NRC webinar': {
        'id': 'eionet-survey-nrc-webinar',
        'title': 'Eionet NRC webinar evaluation survey',
        'description': ('Thank you for completing this form. Your comments are'
                        ' useful for strengthening EEA/Eionet cooperation. '
                        'This evaluation form covers the NRC/Eionet webinar in'
                        ' 2015.'),
        'questions': [
            {'meta_type': 'Naaya Checkboxes Widget',
             'title': 'I am participating as',
             'choices': ['NFP (including NFP alternates and assistants)',
                         'ETC', 'NRC', 'Other Participant'],
             'sortorder': 1,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('How many Eionet-relevant webinars in this topic '
                       'area have you participated in?'),
             'choices': ['First time', '2-5 times', '6-10 times',
                         'More than 10 times'],
             'sortorder': 2,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('1.1. How do you rate this webinar overall in terms of '
                       'usefulness?'),
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'sortorder': 3,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('1.2. How do you rate this webinar overall in terms of '
                       'organisation?'),
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'sortorder': 4,
             'required': False},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '2. Meeting objectives and agendas',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': [('2.1 Were the objectives and agenda of this webinar '
                       'clear?'),
                      '2.2 Do you think the background materials are useful?',
                      '2.3 Were the presentations clear?',
                      '2.4 Facilitation / Chairing'],
             'sortorder': 5,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('2.6 Additional comments on the scope and clarity of '
                       'this webinar agenda'),
             'sortorder': 6,
             'rows': 5},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '3. Organisational aspects',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': ['3.1 Organisational arrangements prior to webinar',
                      '3.2 NRC/Eionet secretariat support',
                      ('3.3 Working conditions during this webinar '
                       '(sound transmission, video transmission, etc.)')
                      ],
             'sortorder': 7,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': '3.4 Are there any aspects which need extra attention?',
             'sortorder': 8,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('3.5 Additional comments on organisational aspects of '
                       'NRC/Eionet webinars'),
             'sortorder': 9,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': '4 Time allocation',
             'sortorder': 10},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('4.1 Length of time allocated to discussions during the'
                       ' webinar'),
             'choices': ['Too short', 'Fine', 'Too long',
                         'I prefer not to answer'],
             'sortorder': 11,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('4.2. Do you find it useful to hold the webinar before'
                       ' the NRC/Eionet workshop?'),
             'choices': ['Yes', 'No', 'I prefer not to answer'],
             'sortorder': 12,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': '4.3 Please explain',
             'sortorder': 13,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': '5 Opinions on NRC/Eionet webinars',
             'sortorder': 14},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('5.1 In your opinion, what was the main benefit of this'
                       ' NRC/Eionet webinar?'),
             'sortorder': 15,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('5.2 Please cite one item (including discussions) that '
                       'worked well in this webinar and explain why.'),
             'sortorder': 16,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('5.3 Which session(s) in this webinar was less useful? '
                       'How would you improve this?'),
             'sortorder': 17,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('6. How many NRC/Eionet webinars would you like to have'
                       ' annually?'),
             'sortorder': 18,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('7. Additional comments (for example usefulness of '
                       'organising more than one webinar between NRC/Eionet '
                       'workshops).'),
             'sortorder': 19,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': 'Thank you!',
             'sortorder': 20},
        ]
    }
}
