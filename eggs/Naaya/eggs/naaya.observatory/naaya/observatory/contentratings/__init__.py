
def initialize(context):
    from zope.configuration import xmlconfig

    import contentratings
    xmlcontext = xmlconfig.file("meta.zcml", contentratings)

    import naaya.observatory.contentratings
    xmlcontext = xmlconfig.file("category.zcml",
            package=naaya.observatory.contentratings,
            context=xmlcontext)

