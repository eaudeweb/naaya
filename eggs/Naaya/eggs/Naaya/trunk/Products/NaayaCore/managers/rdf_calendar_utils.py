__doc__ = """Helper functions for RDFCalendar and RDFSummary Products

"""

import calendar
from DateTime import DateTime

date_format = '%Y-%m-%dT%H:%M:%SZ'

def rdf_cataloged_items(self, meta_type, relations=None, year=None, month=None,
                        day=None, lang=None):
    """Returns a list of dicts that is handled in RDFCalendar.
    This function is usually called via a Script (Python) in RDFCalendar
    Has similar functionality with RDFSummary product, but for Catalogued
    Products.

    Arguments:

      * meta_type -- Usualy 'Naaya Event'
      * relations -- The relation between the fields of the object and the fields
                 of the dictionary that is to be returned
      * lang -- Default language
      * year, month, day -- filtering used to search

    """
    
    if relations is None: #Default relations for Naaya Event content type
        relations = {
            'author': 'contributor', 'subtitle': 'title',
            'dc_description': 'description', 'summary': 'description',
            'dc_coverage': 'coverage', 'id': 'absolute_url',
            'dc_identifier': 'absolute_url', 'link': 'absolute_url',
            'rdfsubject': 'absolute_url', 'dc_type': 'meta_label',
            'type': 'meta_label', 'startdate': 'start_date',
            'enddate': 'end_date',
        }
    elif not isinstance(relations, dict):
        raise ValueError('relations is not a dict')

    if lang is None:
        lang = self.getSite().gl_get_selected_language()



    def cgetattr(ob, name, *argv):
        """ Call getattr result if callable """
        attr = getattr(ob, name, *argv)
        if callable(attr):
            return attr()
        else:
            return attr

    keys = ('author', 'creator', 'dc_coverage', 'dc_description', 'dc_format',
    'dc_identifier', 'dc_source', 'dc_type', 'enddate', 'id', 'language',
    'link', 'location', 'link', 'location', 'organizer', 'publisher',
    'rdfsubject', 'rights', 'startdate', 'subtitle', 'summary', 'title',
    'type', 'updated', ) #Required dict keys in returned dictionaries

    default_values = {
        'dc_format': u'text',
    }

    items = []
    query_dict = None
    year = int(year)
    month = int(month)
    if day:
        day = int(day)
        dates = [DateTime(year, month, day, 0, 0, 0),
                 DateTime(year, month, day, 23, 59, 59), ]
    else:
        dates = [DateTime(year, month, 1, 0, 0, 0),
                 DateTime(year, month,
                          calendar.monthrange(year, month)[1], 23, 59, 59 ), ]

    search_results = set()
    results = self.getSite().getCatalogedObjectsCheckView(meta_type=\
        meta_type, start_date={'query': dates, 'range': 'max'})
    search_results.update(results)
    results = self.getSite().getCatalogedObjectsCheckView(meta_type=\
        meta_type, end_date={'query': dates,  'range': 'min'})
    search_results.update(results)

    for ob in search_results:
        item = {}
        for key in keys:
            if key in relations:
                get_key = relations[key]
            else:
                get_key = key
            if key == 'updated':
                item['updated'] = ob.bobobase_modification_time().strftime(date_format)
            else:
                value = cgetattr(ob, get_key, u'')
                if value is None:
                    value = u''
                if not value and key in default_values.keys():
                    value = default_values[key]
                if isinstance(value, DateTime):
                    value = value.strftime(date_format)
                item[key] = value
        items.append(item)

    return items
