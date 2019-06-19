from eea.ldapadmin.countries import get_country, load_countries


def get_country_name(code):
    """ """
    if code is None:
        return '-'
    country = get_country(code)
    if country['name']:
        return country['name']
    else:
        return code


def get_countries():
    return sorted(
        [(country['code'], country['name']) for country in load_countries()],
        key=lambda x: x[1])
