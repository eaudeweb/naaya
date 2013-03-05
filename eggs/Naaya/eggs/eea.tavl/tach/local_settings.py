HOSTNAME = "http://localhost:8000"

DATABASES = {
    'default': {
        'ENGINE': 'django_hstore.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tach',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True

DEFAULT_USER = {
    'phone': '',
    'first_name': 'Dragos',
    'last_name': 'Catarahia',
    'email': 'dragos.catarahia@gmail.com',
}

DEFAULT_USER_ID = 'catardra'
