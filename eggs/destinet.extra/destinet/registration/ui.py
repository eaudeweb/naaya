""" User interface methods (views) regarding registration in Destinet """
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

def create_destinet_account_html(context, request):
    """ """
    ns = {'here': context}
    widget_inits = [('geo_location', Geo()),
                    ('postaladdress', ''),
                    ('geo_type', ''),
                    ('coverage', ''),
                    ('administrative_level', ''),
                    ('landscape_type', ''),
                    ('topics', ''),
                    ]
    schema = context.portal_schemas['NyContact']
    widgets = [ (schema["%s-property" % w[0]], w[1]) for w in widget_inits ]

    ns = {'widgets': widgets,
          'here': context}
    return context.getFormsTool().getContent(ns, 'site_createaccount')
