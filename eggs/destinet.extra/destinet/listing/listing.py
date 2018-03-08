from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

NaayaPageTemplateFile('zpt/topic', globals(), 'destinet_topics_listing')
NaayaPageTemplateFile('zpt/quickfinder', globals(),
                      'destinet_quickfinder_listing')
NaayaPageTemplateFile('zpt/green_travel_maps', globals(),
                      'destinet_green_travel_maps_listing')

""" User interface methods (views) used for the custom listing """

META_TYPES = [
    'Naaya Youtube', 'Naaya Certificate', 'Naaya Contact', 'Naaya News',
    'Naaya Story', 'Naaya Best Practice', 'Naaya Blob File', 'Naaya Document',
    'Naaya Pointer', 'Naaya Event', 'Naaya URL', 'Naaya Publication',
    'Naaya File'
]

RESOURCE_META_TYPES = [
    'Naaya News', 'Naaya Best Practice', 'Naaya Blob File', 'Naaya Pointer',
    'Naaya Event', 'Naaya URL', 'Naaya Publication', 'Naaya File',
    'Naaya Certificate'
]

META2FRIENDLY = {
    'Naaya Youtube': 'Youtube Video',
    'Naaya Certificate': 'Certificate',
    'Naaya Contact': 'Contact',
    'Naaya News': 'News Item',
    'Naaya Story': 'Story Item',
    'Naaya Best Practice': 'Best Practice',
    'Naaya Blob File': 'File',
    'Naaya File': 'File',
    'Naaya Document': 'Document',
    'Naaya Pointer': 'Pointer',
    'Naaya Event': 'Event',
    'Naaya URL': 'URL',
    'Naaya Publication': 'Publication'
}

RESOURCE_FRIENDLY_NAMES = {
    'News Item': ['Naaya News'],
    'Certificate': ['Naaya Certificate'],
    'Best Practice': ['Naaya Best Practice'],
    'File': ['Naaya Blob File', 'Naaya File'],
    'Pointer': ['Naaya Pointer'],
    'Event': ['Naaya Event'],
    'URL': ['Naaya URL'],
    'Publication': ['Naaya Publication']
}

CERTIFICATE_KEYWORDS = (
    ('Alpine Pearls', 'Alpine Pearls'),
    ('austrian ecolabel', 'Austrian Ecolabel'),
    ('Biohotels', 'Biohotels'),
    ('Biosph\xc3\xa4rengastgeber', 'Biosph\xc3\xa4rengastgeber'),
    ('Blaue Schwalbe', 'Blaue Schwalbe'),
    ('BR-Bliesgau', 'BR-Bliesgau'),
    ('CGH', 'CGH'),
    ('DEHOGA-Umweltcheck', 'DEHOGA-Umweltcheck'),
    ('eco certification malta', 'ECO certification Malta'),
    ('eco-romania', 'ECO Romania'),
    ('ecocamping', 'Ecocamping'),
    ('ecolabel luxemburg', 'Ecolabel Luxemburg'),
    ('Fzn', 'FZN'),
    ('green globe', 'Green globe'),
    ('green key', 'Green key'),
    ('greenpearls', 'Green Pearls'),
    ('Greensign', 'GreenSign'),
    ('GTBS', 'GTBS'),
    ('QualityCoast Award', 'QualityCoast Award'),
    ('lapalmaclub', 'Lapalmaclub'),
    ('lt-c', 'LT-C'),
    ('NP-SH-Wattenmeer', 'NP-SH-Wattenmeer'),
    ('terresdelebro', 'Terresdelebro'),
    ('TourCert', 'TourCert'),
    ('Viabono', 'Viabono'),
)


def get_object_types(context, request):
    """ """
    return RESOURCE_FRIENDLY_NAMES.keys()


def get_content(context, request):
    """ """
    catalog = context.getCatalogTool()
    form = context.REQUEST.form
#    sort_by = int(form.get('order[0][column]'))
    asc = form.get('order[0][dir]')
    if asc == 'asc':
        reversed = True
    else:
        reversed = False

    length = int(form.get('length'))
    start = int(form.get('start'))
    search = form.get('search[value]').decode('utf-8').strip()
    topics = form.get('topic')
    if isinstance(topics, basestring):
        topics = [topics]
    targets = form.get('columns[3][search][value]') or form.get(
        'target_groups')
    meta_type = form.get('meta_type')
    if not meta_type:
        friendly_name = form.get('columns[0][search][value]')
        if friendly_name:
            meta_type = RESOURCE_FRIENDLY_NAMES.get(friendly_name)
    if not meta_type:
        meta_type = RESOURCE_META_TYPES
    query = {'approved': True}
    if topics:
        query['topics'] = topics
    if meta_type:
        query['meta_type'] = meta_type
    if targets:
        if targets == 'all':
            targets = [node.id
                       for node in context.get_list_nodes('target-groups')]
        query['target-groups'] = targets
    all_objects = catalog(**query)
    if search:
        query['title'] = '*' + search + '*'
        objects = catalog(**query)
    else:
        objects = all_objects
    objects = [ob for ob in objects]
    objects.sort(key=lambda x: context.rstk['uni_decode'](
        x.title.strip('"\' ').lower()) or x.id, reverse=reversed)
    page_brains = objects[start:start + length]
    page_objects = [brain.getObject() for brain in page_brains]

    data = []
    for ob in page_objects:
        ob_details = {
            'name': {'url': ob.absolute_url()},
            'meta_type': META2FRIENDLY.get(ob.meta_type)
        }
        if ob.item_has_title(context, ob.title):
            # weirdly enough this means the object doesn't have a title in
            # English and we search for a title in other languages
            for lang in context.gl_get_languages_map():
                if ob.getLocalProperty('title', lang['id']):
                    ob_details['name']['translated'] = {
                        'id': lang['id'], 'title': lang['title']}
                    ob_details['name']['title'] = ob.getId()
                    ob_details['coverage'] = ob.getLocalProperty(
                        'coverage', lang['id']
                    ).strip(', ') or ob.getLocalProperty(
                        'coverage', 'en').strip(', ')
                    break
        else:
            ob_details['name']['translated'] = {'id': '', 'title': ''}
            ob_details['name']['title'] = ob.title
            ob_details['coverage'] = ob.getLocalProperty(
                'coverage', context.gl_get_selected_language()
            ).strip(', ') or ob.getLocalProperty('coverage', 'en').strip(', ')
        if targets:
            ob_details['target-groups'] = ', '.join([context.get_node_title(
                'target-groups', target)
                for target in getattr(ob, 'target-groups')])
        data.append(ob_details)

    return context.rstk['json_dumps']({
        'data': data,
        'draw': int(form.get('draw')),
        'recordsTotal': len(all_objects),
        'recordsFiltered': len(objects),
    })


def change_to_english(context, request):
    """
    Change to english if the user didn't specifically change to another
    language.
    Called in the standard template, it only applies for specific users
    """
    if not request.cookies.get('LOCALIZER_LANGUAGE'):
        context.getSite().portal_i18n.get_negotiator().change_language(
            'en', context, request)
    return


def map_list_locations(context, request, **kw):
    """ make list_locations available outside of portal_map """
    return context.getGeoMapTool().list_locations(request, **kw)


def get_keywords(context, request):
    """ return main keywords for map filtering in Green Travel Maps """
    return CERTIFICATE_KEYWORDS
