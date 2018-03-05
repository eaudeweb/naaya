REF_TREES = [
    ('certificate_credibility',
     {'3rd-party-audit': '3rd party audit',
      'desk-random-audit': 'Desk, random or 2nd party audit',
      'gstc-accredited': 'GSTC accredited',
      'unspecified': 'Unspecified'}
     ),
    ('certificate_services',
     {'certified-tourism-map': 'Certified tourism map on Tourism 2030',
      'standard-published': 'Standard published online for free',
      'more': 'More services',
      'unspecified': 'Unspecified'}
     ),
    ('certificate_sustainability',
     {'comprehensive': 'Comprehensive',
      'environmental': 'Environmental',
      'gstc-recognised': 'GSTC recognised',
      'unspecified': 'Unspecified'}
     )
]

KEYWORD_INDEXES = ['category', 'sustainability', 'certificate_services']
UPDATE_INDEXES = [
    {'id': 'administrative_level',
     'type': 'KeywordIndex',
     'extra': {}},
    {'id': 'coverage',
     'type': 'TextIndexNG3',
     'extra': {'default_encoding': 'utf-8'}},
    {'id': 'geo_type',
     'type': 'FieldIndex',
     'extra': {}},
]
