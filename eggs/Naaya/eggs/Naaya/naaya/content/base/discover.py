def _get_content_types():
    """ make sure _discover_content_types has been run, and return its output """
    from meta import NaayaContent
    nyct = NaayaContent()
    return {
            'content': nyct.contents,
            'constants': nyct.constants,
            'misc_': nyct.misc,
        }

def get_constant(name):
    """ returns a constant of the form METATYPE_*** or PERMISSION_ADD_*** """
    return _get_content_types()['constants'][name]

def get_pluggable_content():
    return _get_content_types()['content']

def initialize(context):
    """ """

    #register classes
    for x in _get_content_types()['content'].values():
        if '_class' not in x:
            # maybe this content type does not want to be registered?
            continue
        context.registerClass(
                x['_class'],
                permission=x['permission'],
                #constructors=(getattr(x['_module'], 'manage_add%s_html' % (x['module'],)),
                #              getattr(x['_module'], 'add%s' % (x['module'],))),
                constructors=x['constructors'],
                icon=x['icon'],
                visibility=None)
