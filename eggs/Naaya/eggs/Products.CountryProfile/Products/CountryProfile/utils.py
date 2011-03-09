import re

def intcomma(value, decimals=False):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    Thanks to Django contributors for the original code. (http://docs.djangoproject.com/en/dev/ref/contrib/humanize/)
    """
    if not isinstance(value, str):
        if decimals:
            value = str(value)
        else:
            value = str("%.0f" % value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', value)
    if value == new:
        return new
    else:
        return intcomma(new)
