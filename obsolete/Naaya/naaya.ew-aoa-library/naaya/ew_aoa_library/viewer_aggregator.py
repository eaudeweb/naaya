# coding=utf-8
from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

viewer_zpt = PageTemplateFile('zpt/view_ag_index.zpt', globals())

class viewer_aggregator(BrowserPage):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, country=None, theme=None):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        if country is not None:
            results = self.aggregate_vl_cf_viewers(country, theme)
        else:
            results = []
        heading_mapping  = self.get_survey_for_headings()
        return viewer_zpt.__of__(ctx)(results=results, heading_mapping=heading_mapping)

    def aggregate_vl_cf_viewers(self, country, theme):
        cf_v = self.context['country-fiches-viewer']
        vl_v = self.context['virtual-library-viewer']

        cf = cf_v.target_survey()
        vl = vl_v.target_survey()

        cf_shadows = cf_v.filter_answers_cf_vl_aggregator(country, theme)
        vl_shadows = vl_v.filter_answers_cf_vl_aggregator(country, theme)

        group_by_document_type = {}
        for shadow in cf_shadows:
            for dt_i in shadow.document_type:
                dtn_i = cf_v.get_normalized_document_type(dt_i)
                group_by_document_type.setdefault(dtn_i, []).append(shadow)
        for shadow in vl_shadows:
            for dt_i in shadow.document_type:
                dtn_i = vl_v.get_normalized_document_type(dt_i)
                group_by_document_type.setdefault(dtn_i, []).append(shadow)

        document_type_names = cf_v.all_document_types
        heading_document_types = self.heading_document_types()

        group_by_heading = {}
        for heading, document_types in heading_document_types.items():
            group_by_heading[heading] = []
            for dt in document_types:
                dt_i = document_type_names.index(dt)
                if dt_i in group_by_document_type:
                    group_by_heading[heading].extend(group_by_document_type[dt_i])
            group_by_heading[heading].sort(key=lambda x: x.publication_year, reverse=True)

        ret = []
        if theme == 'Water':
            for heading in self.water_headings_in_order():
                if heading in group_by_heading and group_by_heading[heading]:
                    ret.append((heading, group_by_heading[heading]))
        else: # theme == 'Green Economy'
            for heading in self.ge_headings_in_order():
                if heading in group_by_heading and group_by_heading[heading]:
                    ret.append((heading, group_by_heading[heading]))

        return ret

    def ge_headings_in_order(self):
        return [
        'Green economy assessment/report',
        'Section in State of Environment report',
        'Sectorial report',
        'Environmental statistics',
        'Environmental indicator set',
        'Section in environmental performance review',
        'Environmental compendium',
        'Library services',
        'Country profiles',
        'Website',
        'National Institution dealing with green economy',
        ]

    def get_survey_for_headings(self):
        cf_v = self.context['country-fiches-viewer']
        vl_v = self.context['virtual-library-viewer']

        cf = cf_v.target_survey()
        vl = vl_v.target_survey()

        return {
        'Section in State of Environment report': [vl],
        'Section in environmental performance review': [vl],
        'State of water assessment/report': [vl],
        'Green economy assessment/report': [vl],
        'Sectorial report': [vl],
        'Water sector or NGOs report': [vl],
        'Water statistics': [vl, cf],
        'Environmental statistics': [vl, cf],
        'Environmental indicator set': [vl, cf],
        'Environmental compendium': [vl, cf],
        'Water indicator set': [vl, cf],
        'Website': [cf],
        'Library services': [cf],
        'Country profiles': [cf],
        'National Institution dealing with water': [cf],
        'National Institution dealing with green economy': [cf],
        }

    def heading_document_types(self):
        return {
        'Section in State of Environment report': ['Section in State of Environment report'],
        'Section in environmental performance review': ['Section in environmental performance review'],
        'State of water assessment/report': ['State of water assessment/report – National level',
                                             'State of water assessment/report – Sub-national level',
                                             'State of water assessment/report – Regional/Global level'],
        'Green economy assessment/report': ['State of green economy assessment/report – National level',
                                                     'State of green economy assessment/report – Sub-national level',
                                                     'State of green economy assessment/report – Regional/Global level'],
        'Sectorial report': ['Sectorial report'],
        'Water sector or NGOs report': ['Water sector or NGOs report'],
        'Water statistics': ['Water statistics'],
        'Environmental statistics': ['Environmental statistics'],
        'Environmental indicator set': ['Environmental indicator set – National',
                                        'Environmental indicator set – Sub-national',
                                        'Environmental indicator set – Regional'],
        'Environmental compendium': ['Environmental compendium'],
        'Water indicator set': ['Water indicator set'],
        'Website': ['Website'],
        'Library services': ['Library services'],
        'Country profiles': ['Country profiles'],
        'National Institution dealing with water': ['National Institution dealing with water'],
        'National Institution dealing with green economy': ['National Institution dealing with green economy'],
        }

    def water_headings_in_order(self):
        return [
        'Section in State of Environment report',
        'Environmental statistics',
        'Environmental indicator set',
        'Environmental compendium',
        'Section in environmental performance review',
        'State of water assessment/report',
        'Water statistics',
        'Water indicator set',
        'Water sector or NGOs report',
        'Library services',
        'Country profiles',
        'Website',
        'National Institution dealing with water',
    ]
