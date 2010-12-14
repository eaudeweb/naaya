def pat(s):
    """ convert from string into a pattern to use with regexps """
    return reduce(lambda s, c: s.replace(c, '\\'+c), '(){}[]', s)

def physical_path(ob):
    return '/'.join(ob.getPhysicalPath())
