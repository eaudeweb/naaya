EIONET_MEETINGS = ['NRC meeting', 'NRC webinar', 'NFP neeting', 'NFP webinar']
EIONET_SURVEYS = {
    'NFP meeting': {
        'id': 'eionet-survey-nfp-meeting',
        'title': 'Eionet NFP meeting evaluation survey',
        'description': ('Thank you for completing the form.'
                        'Your comments will be very useful in strengthening '
                        'EEA/Eionet cooperation. This evaluation form covers '
                        'all meetings in 2015.'),
        'questions': [
            {'meta_type': 'Naaya Checkboxes Widget',
             'title': 'I am attending the NFP/Eionet meeting as',
             'choices': ['NFP (including NFP alternates and assistants)',
                         'ETC',
                         'Other Participant'],
             'sortorder': 1,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': 'I am attending the NFP/Eionet meeting',
             'choices': ['For the first time',
                         '2-6 times',
                         '7-10 times',
                         'More than 10 times'],
             'sortorder': 2,
             'required': False},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '1. General',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': [('1.1. How do you rate this NFP/Eionet meeting in '
                       'terms of usefulness?'),
                      ('1.2. How do you rate this NFP/Eionet meeting in '
                       'terms of organisation?')],
             'sortorder': 3,
             'required': False},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '2. Meeting agenda and objectives',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': [('2.1 Are the objectives and agenda of the NFP/Eionet '
                       'meeting clear?'),
                      '2.2 Are the background materials relevant?',
                      '2.3 Facilitation / Chairing',
                      ('2.4 Have the objectives of each session been achieved?'
                       ),
                      '2.5 Is the right mixture of topics covered?'],
             'sortorder': 4,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('2.6. Additional comments on the scope and clarity of '
                       'NFP/Eionet meeting agendas'),
             'sortorder': 5,
             'rows': 5},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '3. Organisational aspects',
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
             'rows': ['3.1 Travel arrangements prior to meeting',
                      '3.2 NFP/Eionet secretariat support',
                      ('3.3 Working conditions during this meeting (conference'
                       ' room facilities, equipment etc.)')],
             'sortorder': 6,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('3.4 Are there any aspects which need extra attention '
                       'when the NFP/Eionet meeting is held outside the EEA? '
                       '(2016 = Turkey)'),
             'sortorder': 7,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('3.5 Additional comments on organisational aspects of '
                       'NFP/Eionet meetings overall'),
             'sortorder': 8,
             'rows': 5},
            {'meta_type': 'Naaya Radio Matrix Widget',
             'title': '4. Time allocation',
             'choices': ['Too short', 'Fine', 'Too long',
                         'I prefer not to answer'],
             'rows': [('4.1 Length of time allocated to discussions during '
                       'the NFP/Eionet meeting'),
                      '4.2 Time for networking',
                      ('4.3 Length of time allocated to presentations and '
                       'lectures during the NFP/Eionet meeting')],
             'sortorder': 9,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('4.4 Do you find it useful to hold the meeting outside'
                       ' Copenhagen occasionally?'),
             'choices': ['Yes', 'No', 'I prefer not to answer'],
             'sortorder': 10,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': '4.5 Please explain',
             'sortorder': 11,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': '5. Opinions on NFP/Eionet meetings',
             'sortorder': 12},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('5.1 In your opinion, what were the main benefits of '
                       'this NFP/Eionet meeting?'),
             'sortorder': 13,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('5.2  Please cite one session (including discussions) '
                       'that worked well at this meeting and explain why.'),
             'sortorder': 14,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('5.3 Which sessions were less useful? '
                       'How would you suggest that EEA improves them?'),
             'sortorder': 15,
             'rows': 5},
            {'meta_type': 'Naaya Text Area Widget',
             'title': '6. Additional comments (for example usefulness of joint'
                      ' meetings with other networks)',
             'sortorder': 16,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': '7. Opinions on NFP/Eionet webinars',
             'sortorder': 17},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('7.1 In your opinion, what were the main benefits of '
                       'NFP/Eionet webinars in 2016?'),
             'sortorder': 18,
             'rows': 5},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('7.2 What do you think of the number of NFP webinars '
                       'per the year? There are:'),
             'choices': ['Too many', 'The  number is fine', 'Too few',
                         'I prefer not to answer'],
             'sortorder': 19,
             'required': False},
            {'meta_type': 'Naaya Radio Widget',
             'title': ('7.3 Do you find the new tools to operate webinar '
                       'user friendly?'),
             'choices': ['Yes', 'No', 'I prefer not to answer'],
             'sortorder': 20,
             'required': False},
            {'meta_type': 'Naaya Text Area Widget',
             'title': ('7.4 Additional comments related to webinars'),
             'sortorder': 19,
             'rows': 5},
            {'meta_type': 'Naaya Label Widget',
             'title': 'Thank you!',
             'sortorder': 20}
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
             'choices': ['Poor', 'Satisfactory', 'Good', 'Excellent',
                         'I prefer not to answer'],
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
                      '3.4 Use of practical examples/ case studies',
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
