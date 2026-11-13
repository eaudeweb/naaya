WIDGET_NAMES = [
    'geo_location',
    'postaladdress',
    'category-organization',
    'category-marketplace',
    'category-supporting-solutions',
    'coverage',
    'administrative_level',
    'landscape_type',
    'topics',

    #'geo_type',
]

# these are the normal field names in register form for an EW Site
EW_REGISTER_FIELD_NAMES = ('firstname', 'lastname', 'email', 'password',
                           'organisation', 'comments', 'location')

USER_GROUPS = {
    'european-ecotourism-network':
        'who-who/civil-society-ngos/european-ecotourism-network/new-applicants',
}

# name of a hidden registration form field that only bots fill in
HONEYPOT_FIELD = 'homepage_url'

# disposable email services refused at registration
BLOCKED_EMAIL_DOMAINS = frozenset([
    '10minutemail.com',
    'chuwel.com',
    'dispostable.com',
    'getnada.com',
    'guerrillamail.com',
    'hidingpost.com',
    'mailinator.com',
    'maildrop.cc',
    'sharklasers.com',
    'temp-mail.org',
    'trashmail.com',
    'yopmail.com',
])
