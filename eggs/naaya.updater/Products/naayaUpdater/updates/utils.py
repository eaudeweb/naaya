def pat(s):
    """ convert from string into a pattern to use with regexps """
    return reduce(lambda s, c: s.replace(c, '\\'+c), '(){}[]', s)
