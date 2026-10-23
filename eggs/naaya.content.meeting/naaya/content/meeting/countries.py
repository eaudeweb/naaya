"""Country names for the participant forms, from countries.json (ISO 3166 codes)."""
import json
import os

with open(os.path.join(os.path.dirname(__file__), 'countries.json'), encoding='utf-8') as f:
    COUNTRIES = json.load(f)


def get_country_name(code):
    """ Get country name """
    if code is None:
        return '-'
    return COUNTRIES.get(code.lower(), code)


def get_countries():
    return sorted(COUNTRIES.items(), key=lambda x: x[1])
