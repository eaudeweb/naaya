import xml.parsers.expat

def get_char_data(data, path):
    """
    >>> get_char_data('<a>1<b>2</b>3</a>', ['a', 'b'])
    [u'2']
    >>> get_char_data('<a>1<b>2<c>3</c>4</b>5</a>', ['a', 'c'])
    [u'3']
    >>> get_char_data('<a>1<b>2<c>3</c>4</b>5</a>', ['a', 'b'])
    [u'2', u'3', u'4']
    """
    matched = []
    values = []
    def start_element(name, attrs):
        i = len(matched)
        if i < len(path) and name == path[i]:
            matched.append(name)
    def end_element(name):
        if len(matched) != 0 and name == matched[-1]:
            matched.pop()
    def char_data(data):
        if len(matched) == len(path):
            values.append(data)

    p = xml.parsers.expat.ParserCreate(encoding='utf-8')
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
    p.Parse(data)

    return values

def get_multiple_char_data(data, main_path, **kwpaths):
    """
    >>> data = '<a>1 <b>2<c>3</c>4<d>5</d>6</b> 7 <e>8</e> 9</a>'
    >>> result = get_multiple_char_data(data, ['a', 'b'], c=['c'], d=['d'])
    >>> len(result)
    1
    >>> result[0]['c']
    u'3'
    >>> result[0]['d']
    u'5'
    """
    main_matched = []
    local_matched = {}
    for k in kwpaths.keys():
        local_matched[k] = []
    def local_empty():
        for k in kwpaths.keys():
            if len(local_matched[k]) > 0:
                return False
        return True
    values = [{}]
    def start_element(name, attrs):
        i = len(main_matched)
        if i < len(main_path) and name == main_path[i]:
            main_matched.append(name)
        elif i == len(main_path):
            for k, path in kwpaths.iteritems():
                j = len(local_matched[k])
                if j < len(path) and name == path[j]:
                    local_matched[k].append(name)
    def end_element(name):
        if local_empty():
            if len(main_matched) == len(main_path) and name == main_matched[-1]:
                values.append({})
            if len(main_matched) > 0 and name == main_matched[-1]:
                main_matched.pop()
        else:
            for k, path in kwpaths.iteritems():
                if len(local_matched[k]) != 0 and name == local_matched[k][-1]:
                    local_matched[k].pop()
    def char_data(data):
        if len(main_matched) == len(main_path):
            for k, path in kwpaths.iteritems():
                if len(local_matched[k]) == len(path):
                    if k not in values[-1]:
                        values[-1][k] = data
                    else:
                        if type(values[-1][k]) != type([]):
                            values[-1][k] = [values[-1][k], data]
                        else:
                            values[-1][k] = values[-1][k].append(data)

    p = xml.parsers.expat.ParserCreate(encoding='utf-8')
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
    p.Parse(data)

    return values[:-1]


def get_title(data):
    path = ['gmd:identificationInfo', 
                'gmd:citation',
                    'gmd:CI_Citation',
                        'gmd:title',
                            'gco:CharacterString']
    values = get_char_data(data, path)
    if len(values) == 0:
        return ''
    return values[0]
    
def get_points_of_contact(data):
    main_path = ['gmd:identificationInfo',
                    'gmd:pointOfContact',
                        'gmd:CI_ResponsibleParty']
    organisation_subpath = ['gmd:organisationName',
                               'gco:CharacterString']
    email_subpath = ['gmd:contactInfo',
                        'gmd:address',
                            'gmd:electronicMailAddress',
                                'gco:CharacterString']
    role_subpath = ['gmd:role',
                        'gmd:CI_RoleCode']
    values = get_multiple_char_data(data, main_path,
                                     organisation=organisation_subpath,
                                     email=email_subpath,
                                     role=role_subpath)
    return values

def get_distribution_info(data):
    path = ['gmd:distributionInfo',
                'gmd:transferOptions',
                    'gmd:onLine',
                        'gmd:linkage',
                             'gmd:URL']
    return get_char_data(data, path)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
