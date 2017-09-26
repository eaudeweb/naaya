# coding=utf-8
from difflib import get_close_matches
try:
    import simplejson as json
except ImportError:
    import json

from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaBase.NyBase import NyBase
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from zope.app.container.interfaces import (IObjectAddedEvent,
                                           IObjectRemovedEvent)
from zope import interface
from zope.component import adapter
from ZPublisher import NotFound
import transaction

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaSurvey.interfaces import INySurveyAnswer, INySurveyAnswerAddEvent
from Products.NaayaCore.CatalogTool.interfaces import INyCatalogAware
from Products.NaayaCore.GeoMapTool.managers import geocoding
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.core.interfaces import INyObjectContainer
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from naaya.core.zope2util import ofs_path

import shadow
from devel import aoa_devel_hook

survey_answer_metatype = 'Naaya Survey Answer'
shadow_metatype = 'Naaya EW_AOA Shadow Object'

def physical_path(obj):
    return '/'.join(obj.getPhysicalPath())

manage_addViewer_html = PageTemplateFile('zpt/manage_add', globals())
def manage_addViewer(parent, id, title, target_path, REQUEST=None):
    """ instantiate the Viewer """
    ob = AoALibraryViewer(id, title, target_path)
    parent._setObject(id, ob)
    if REQUEST is not None:
        url = '%s/manage_workspace' % parent.absolute_url()
        REQUEST.RESPONSE.redirect(url)

topics_to_themes = {
                    'a':'w_water-resources-topics',
                    'b':'w_water-resource-management-topics',
                    'c':'w_green-economy-topics',
                    'd':'w_resource-efficiency-topics'
                    }

class AoALibraryViewer(SimpleItem, NyBase):
    interface.implements(INyCatalogAware, INyObjectContainer)

    meta_type = "Naaya EW_AOA Library Viewer"

    manage_options = (
        {'label': 'Summary', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
        {'label':'Updates', 'action':'manage_update_html'},
    ) + SimpleItem.manage_options


    all_document_types = [
        'Please select', #0
        'Section in State of Environment report', #1
        'Section in environmental performance review', #2
        'State of water assessment/report – National level', #3
        'State of water assessment/report – Sub-national level', #4
        'State of water assessment/report – Regional/Global level', #5
        'State of green economy assessment/report – National level', #6
        'State of green economy assessment/report – Sub-national level', #7
        'State of green economy assessment/report – Regional/Global level', #8
        'Sectorial report', #9
        'Water sector or NGOs report', #10
        'Water statistics', #11
        'Environmental statistics', #12
        'Environmental indicator set – National', #13
        'Environmental indicator set – Sub-national', #14
        'Environmental indicator set – Regional', #15
        'Environmental compendium', #16
        'Water indicator set', #17
        'Website', #18
        'Library services', #19
        'Country profiles', #20
        'National Institution dealing with water', #21
        'National Institution dealing with green economy', #22
    ]
    water_document_types = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    ge_document_types = [1, 2, 6, 7, 8, 9, 12, 13, 14, 15, 16, 18, 19, 20, 22]

    water_themes = shadow.water_themes
    ge_themes = shadow.ge_themes

    security = ClassSecurityInfo()

    def __init__(self, id, title, target_path):
        self._setId(id)
        self.title = title
        self.target_path = target_path

    security.declareProtected(view, 'target_survey')
    def target_survey(self):
        return self.getSite().restrictedTraverse(self.target_path)

    security.declarePrivate('wrap_answer')
    def wrap_answer(self, answer):
        #aoa_devel_hook(shadow.__name__)

# disable the cache (-- moregale)
#        if not hasattr(self, '_v_shadow_cache') or Globals.DevelopmentMode:
#            self._v_shadow_cache = {}
#
#        # Survey answers are, in effect, immutable. So we cache them by path.
#        key = '/'.join(answer.getPhysicalPath())
#        try:
#            obj = self._v_shadow_cache[key]
#        except KeyError:
#            obj = shadow.shadow_for_answer(answer)
#            self._v_shadow_cache[key] = obj

        obj = shadow.shadow_for_answer(answer)
        return obj.__of__(self)

    security.declareProtected(view, 'iter_assessments')
    def iter_assessments(self, show_unapproved=True, show_drafts=False):
        survey = self.target_survey()
        for answer in survey.objectValues(survey_answer_metatype):
            if answer.is_draft() and not show_drafts:
                continue
            if not hasattr(answer, 'approved_date') and not show_unapproved:
                continue
            yield self.wrap_answer(answer)

    security.declareProtected(view, 'objectValues')
    def objectValues(self):
        return list(self.iter_assessments())

    def __getitem__(self, key):
        survey = self.target_survey()
        answer = survey[key]
        if answer.meta_type != survey_answer_metatype:
            raise KeyError
        if answer.is_draft():
            raise KeyError
        return self.wrap_answer(answer)

    def get_survey_answer(self, key):
        survey = self.target_survey()
        if key not in survey.objectIds(survey_answer_metatype):
            raise KeyError
        if survey[key].is_draft():
            raise KeyError
        return survey[key]

    security.declareProtected(view_management_screens, 'manage_recatalog')
    def manage_recatalog(self, REQUEST=None):
        """ recatalog our shadow objects """
        catalog = self.getSite().getCatalogTool()
        self_path = physical_path(self)
        for p in [b.getPath() for b in catalog(path=self_path)]:
            if p == self_path:
                continue
            catalog.uncatalog_object(p)

        self._v_shadow_cache = {} # clear the cache
        for shadow in self.iter_assessments():
            catalog.catalog_object(shadow, physical_path(shadow))

        if REQUEST is not None:
            url = '%s/manage_workspace' % self.absolute_url()
            REQUEST.RESPONSE.redirect(url)

    _index_html = NaayaPageTemplateFile('zpt/index', globals(),
                            'naaya.ew_aoa_library.viewer.index_html')

    security.declareProtected(view, 'index_html')
    def index_html(self, filter=True, **kwargs):
        """ """
        if not kwargs:
            shadows = list(self.iter_assessments())
            filter = False
            kwargs['shadows'] = shadows
        kwargs['filter'] = filter
        return self._index_html(**kwargs)

    manage_main = PageTemplateFile('zpt/manage_main', globals())

    security.declarePublic('approved_date')
    def approved_date(self, answer):
        survey_answer = self.get_survey_answer(answer.getId())
        return getattr(survey_answer, 'approved_date', False)

    security.declareProtected(view_management_screens, 'manage_update_html')
    def manage_update_html(self, REQUEST=None):
        """ Update RT answer report title
        based on the available report titles from the VL"""
        if not REQUEST.form.has_key('submit'):
            return self._manage_update_html()
        state = {}
        state['updated_answers'] = {}
        state['errors'] = {}
        state['orphan_answers'] = []
        state['already_updated'] = []
        review_template = self.aq_parent['tools']['general_template']['general-template']
        library = self.aq_parent['tools']['virtual_library']['bibliography-details-each-assessment']
        country_fiches = self.aq_parent['tools']['country_fiches']
        update_type = REQUEST.form.get('update_type')
        if update_type == 'update_vl_approval':
            self._update_vl_approval(state, library)
        if update_type == 'update_rt_titles':
            self._update_rt_titles(state, review_template, library)
        if update_type == 'update_remove_acronyms':
            self._update_remove_acronyms(state, review_template)
        if update_type == 'update_vl_countries_and_region':
            self._update_vl_countries_and_region(state, review_template, library)
        if update_type == 'update_vl_id_in_rt':
            self._update_vl_id_in_rt(state)
        if update_type == 'update_vl_countries':
            self._update_vl_countries(state, library)
        if update_type == 'update_cf_countries':
            self._update_cf_countries(state, country_fiches)
        if update_type == 'update_cf_types_of_documents':
            self._update_cf_types_of_documents(state, country_fiches)
        if update_type == 'update_remove_please_select_type_of_document':
            self._update_remove_please_select_type_of_document(state, library, country_fiches)
        if update_type == 'update_to_multiple_types_of_documents':
            self._update_to_multiple_types_of_documents(state, library, country_fiches)
        if update_type == 'update_vl_regions':
            self._update_vl_regions(state, library)
        if update_type == 'update_creation_date':
            self._correct_creation_date(state, library)
        return self._manage_update_html(updated_answers=state['updated_answers'],
            errors=state['errors'].items(),
            orphan_answers=state['orphan_answers'], already_updated=state['already_updated'])

    _manage_update_html = PageTemplateFile('zpt/viewer_manage_update', globals())

    def _correct_creation_date(self, state, library):
        """ """
        for vl_answer in library.objectValues(survey_answer_metatype):
            if vl_answer.get('creation_date') is DateTime:
                setattr(vl_answer, 'creation_date', None)
                state['updated_answers'][vl_answer.absolute_url()] = []

    def _update_vl_regions(self, state, library):
        """ """
        def regions_string_to_list(region_val):
            if not region_val:
                return []

            ret = []
            for rs1 in region_val.split(','):
                for rs2 in rs1.split(' and '):
                    for r in rs2.split(' ans '):
                        ret.append(r.strip())
            return ret

        region_list = ['Caucasus', 'Central Asia', 'Eastern Europe',
                       'EEA member countries', 'Russian Federation',
                       'Western Balkans',
                       'Africa', 'Asia', 'Global', 'Middle East',
                       'North America', 'Northen Africa', 'Pacific countries',
                       'other European', 'other OECD countries']

        mapping = dict([(region, i) for i, region in enumerate(region_list)])
        mapping['Rssuian Federation'] = mapping['Russian Federation']
        mapping['North of America'] = mapping['North America']

        # update the question information
        from Products.NaayaSurvey.migrations import basic_replace
        from Products.NaayaWidgets.widgets.CheckboxesWidget import addCheckboxesWidget
        new_widget = basic_replace(library, 'w_geo-coverage-region', addCheckboxesWidget)
        new_widget._setLocalPropValue('choices', 'en', region_list)
        new_widget._setLocalPropValue('choices', 'ru', region_list)

        for vl_answer in library.objectValues(survey_answer_metatype):
            region_val = vl_answer.get('w_geo-coverage-region')
            if isinstance(region_val, list):
                state['already_updated'].append(vl_answer.absolute_url())
            else:
                regions = regions_string_to_list(region_val)
                for region in regions:
                    if region not in mapping:
                        state['errors'][vl_answer.absolute_url()] = \
                                'Not matched %s' % region
                        break
                else:
                    value = [mapping[r] for r in regions]
                    vl_answer.set_property('w_geo-coverage-region',
                            sorted(set(value)))
                    state['updated_answers'][vl_answer.absolute_url()] = \
                            regions

    security.declarePublic('get_close_answers')
    def get_close_answers(self, title_en, title_ru, year, original_title):
        """ """
        def string_to_match(title):
            if title.startswith("Google translation: "):
                title = title[len("Google translation: "):]
            ret = title.lower()
            for c in ' -/().,;!?':
                ret = ret.replace(c, '')
            return ret

        def get_close_answers_by_lang_title(shadows, title, lang):
            shadows_by_title = dict((string_to_match(shadow.get('title', lang)),
                                        shadow)
                                    for shadow in shadows)

            matched_titles = get_close_matches(string_to_match(title),
                                                shadows_by_title.keys(),
                                                n=5, cutoff=0.5)
            return [{'title': shadows_by_title[t].get('title', lang),
                     'answer_url': shadows_by_title[t].target_answer().absolute_url()}
                     for t in matched_titles]

        def get_close_answers_by_lang_original(shadows, title, lang):
            shadows_by_title = dict((string_to_match(shadow.original_title[lang]),
                                        shadow)
                                    for shadow in shadows
                                    if lang in shadow.original_title)

            matched_titles = get_close_matches(string_to_match(title),
                                                shadows_by_title.keys(),
                                                n=5, cutoff=0.9)
            return [{'title': shadows_by_title[t].original_title[lang],
                     'answer_url': shadows_by_title[t].target_answer().absolute_url()}
                     for t in matched_titles]
        ret = []

        catalog = self.getSite().getCatalogTool()
        brains = catalog(path=ofs_path(self), viewer_year=year)
        shadows = [b.getObject() for b in brains]

        if original_title:
            original_title_map = shadow.extract_original_title_dict(original_title)
            for lang in original_title_map:
                ret.extend(get_close_answers_by_lang_original(shadows,
                                            original_title_map[lang],
                                            lang))

        if title_en:
            ret.extend(get_close_answers_by_lang_title(shadows, title_en, 'en'))
        if title_ru:
            ret.extend(get_close_answers_by_lang_title(shadows, title_ru, 'ru'))

        return json.dumps(ret)

    def _update_to_multiple_types_of_documents(self, state, library, country_fiches):
        # update the question information
        from Products.NaayaSurvey.migrations import basic_replace
        from Products.NaayaWidgets.widgets.CheckboxesWidget import addCheckboxesWidget

        def do_update(survey):
            document_types = survey['w_type-document'].getChoices()
            new_widget = basic_replace(survey, 'w_type-document', addCheckboxesWidget)
            new_widget._setLocalPropValue('choices', 'en', document_types)
            new_widget._setLocalPropValue('choices', 'ru', document_types)

            for answer in survey.objectValues(survey_answer_metatype):
                old_type_of_document = answer.get('w_type-document')
                if isinstance(old_type_of_document, list):
                    continue

                if old_type_of_document is None:
                    answer.set_property('w_type-document', [])
                else:
                    answer.set_property('w_type-document', [old_type_of_document])

                state['updated_answers'][answer.absolute_url()] = ['Updated from %r to %r' % (old_type_of_document, answer.get('w_type-document'))]

        do_update(library)
        do_update(country_fiches)


    def _update_remove_please_select_type_of_document(self, state, library, country_fiches):
        def do_update(survey):
            document_types = survey['w_type-document'].getChoices()
            if document_types[0] != 'Please select':
                return

            survey['w_type-document']._setLocalPropValue('choices', 'en', document_types[1:])
            survey['w_type-document']._setLocalPropValue('choices', 'ru', document_types[1:])

            for answer in survey.objectValues(survey_answer_metatype):
                old_type_of_document = answer.get('w_type-document')
                if old_type_of_document == 0 or old_type_of_document is None:
                    answer.set_property('w_type-document', None)
                else:
                    answer.set_property('w_type-document', old_type_of_document - 1)

                state['updated_answers'][answer.absolute_url()] = ['Updated from %r to %r' % (old_type_of_document, answer.get('w_type-document'))]

        do_update(library)
        do_update(country_fiches)

    def _update_cf_types_of_documents(self, state, country_fiches):
        cf_types_of_docuements = [
            'Please select',
            'Water sector or NGOs report',
            'Water statistics',
            'Environmental statistics',
            'Environmental indicator set – National',
            'Environmental indicator set – Sub-national',
            'Environmental indicator set – Regional',
            'Environmental compendium',
            'Water indicator set',
            'Website',
            'Library services',
            'Country profiles',
            'National Institution dealing with water',
            'National Institution dealing with green economy',
        ]
        savepoint = transaction.savepoint()

        widget = getattr(country_fiches.aq_base, 'w_type-document')
        old_types_of_documents = widget.getChoices()

        for cf_answer in country_fiches.objectValues(survey_answer_metatype):
            old_type_of_document = old_types_of_documents[cf_answer.get('w_type-document')]
            try:
                new_type_of_document = cf_types_of_docuements.index(old_type_of_document)
            except ValueError:
                state['errors'][cf_answer.absolute_url()] = 'Not matched %s' % old_type_of_document
            else:
                cf_answer.set_property('w_type-document', new_type_of_document)
                state['updated_answers'][cf_answer.absolute_url()] = [cf_types_of_docuements[new_type_of_document]]

        widget._setLocalPropValue('choices', 'en', cf_types_of_docuements)
        widget._setLocalPropValue('choices', 'ru', cf_types_of_docuements)

        if state['errors']:
            savepoint.rollback()


    def _update_cf_countries(self, state, country_fiches):
        country_list = [
        "Albania",
        "Andorra",
        "Armenia",
        "Austria",
        "Azerbaijan",
        "Belarus",
        "Belgium",
        "Bosnia and Herzegovina",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Georgia",
        "Germany",
        "Greece",
        "Hungary",
        "Iceland",
        "Ireland",
        "Italy",
        "Kazakhstan",
        "Kyrgyzstan",
        "Latvia",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Former Yugoslav Republic of Macedonia",
        "Malta",
        "Republic of Moldova",
        "Monaco",
        "Montenegro",
        "the Netherlands",
        "Norway",
        "Poland",
        "Portugal",
        "Romania",
        "Russian Federation",
        "San Marino",
        "Serbia",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Switzerland",
        "Tajikistan",
        "Turkey",
        "Turkmenistan",
        "Ukraine",
        "the United Kingdom",
        "Uzbekistan",
        "Kosovo under un security council 1244/9950",
        ]

        widget = getattr(country_fiches.aq_base, 'w_country')
        old_countries = widget.getChoices()
        widget._setLocalPropValue('choices', 'en', country_list)
        widget._setLocalPropValue('choices', 'ru', country_list)

        for cf_answer in country_fiches.objectValues(survey_answer_metatype):
            old_country_val = cf_answer.get('w_country')
            new_country_val = []
            for c_i in old_country_val:
                new_country_val.append(country_list.index(old_countries[c_i]))
            cf_answer.set_property('w_country', new_country_val)
            state['updated_answers'][cf_answer.absolute_url()] = map(lambda x: country_list[x], new_country_val)


    def _update_vl_countries(self, state, library):
        country_list = [
        "Albania",
        "Andorra",
        "Armenia",
        "Austria",
        "Azerbaijan",
        "Belarus",
        "Belgium",
        "Bosnia and Herzegovina",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Georgia",
        "Germany",
        "Greece",
        "Hungary",
        "Iceland",
        "Ireland",
        "Italy",
        "Kazakhstan",
        "Kyrgyzstan",
        "Latvia",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Former Yugoslav Republic of Macedonia",
        "Malta",
        "Republic of Moldova",
        "Monaco",
        "Montenegro",
        "the Netherlands",
        "Norway",
        "Poland",
        "Portugal",
        "Romania",
        "Russian Federation",
        "San Marino",
        "Serbia",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Switzerland",
        "Tajikistan",
        "Turkey",
        "Turkmenistan",
        "Ukraine",
        "the United Kingdom",
        "Uzbekistan",
        "Kosovo under un security council 1244/9950",
        "Afghanistan",
        "Algeria",
        "Australia",
        "Brazil",
        "Cambodia",
        "Cameroun",
        "Canada",
        "China",
        "Costa Rica",
        "Egypt",
        "Honduras",
        "India",
        "Indonesia",
        "Iran",
        "Israel",
        "Japan",
        "Jordan",
        "Kenya",
        "Korea",
        "Lebanon",
        "Libya",
        "Mauritius",
        "Morocco",
        "Nepal",
        "Nigeria",
        "Palestinian territory",
        "Singapore",
        "Syria",
        "Tunisia",
        "Uganda",
        "USA",
        "others", # San Marino, Andorra, Monaco
        ]

        # update the question information
        from Products.NaayaSurvey.migrations import basic_replace
        from Products.NaayaWidgets.widgets.CheckboxesWidget import addCheckboxesWidget
        new_widget = basic_replace(library, 'w_official-country-region', addCheckboxesWidget)
        new_widget._setLocalPropValue('choices', 'en', country_list)
        new_widget._setLocalPropValue('choices', 'ru', country_list)

        mapping = dict([(country, i) for i, country in enumerate(country_list)])
        mapping['Belgium (the Region of Flanders)'] = mapping['Belgium']
        mapping['Bosnia-Herzegovina'] = mapping['Bosnia and Herzegovina']
        mapping['Bosnia'] = mapping['Bosnia and Herzegovina']
        mapping['Brasil'] = mapping['Brazil']
        mapping['Herzegovina'] = mapping['Bosnia and Herzegovina']
        mapping['Croati'] = mapping['Croatia']
        mapping['the Czech Republic'] = mapping['Czech Republic']
        mapping['Germany.'] = mapping['Germany']
        mapping['Kosovo'] = mapping['Kosovo under un security council 1244/9950']
        mapping['FYR of Macedonia'] = mapping['Former Yugoslav Republic of Macedonia']

        mapping['Moldova'] = mapping['Republic of Moldova']
        mapping['Monako'] = mapping['Monaco']
        mapping['Netherlands'] = mapping['the Netherlands']
        mapping['Russia Federation'] = mapping['Russian Federation']
        mapping['Russia'] = mapping['Russian Federation']
        mapping['Slovak Republic'] = mapping['Slovakia']
        mapping['United Kingdom'] = mapping['the United Kingdom']
        mapping['others.'] = mapping['others']

        mapping['Caucasus'] = ['Armenia', 'Azerbaijan', 'Georgia']
        mapping['Eastern Europe'] = ['Belarus', 'Moldova', 'Ukraine']
        mapping['Central Asia'] = ['Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Uzbekistan']

        ignored = set([""])

        for vl_answer in library.objectValues(survey_answer_metatype):
            country_val = vl_answer.get('w_official-country-region')
            if isinstance(country_val, list):
                state['already_updated'].append(vl_answer.absolute_url())
            else:
                # hardcoded
                if not country_val:
                    vl_answer.set_property('w_official-country-region', [])
                    state['updated_answers'][vl_answer.absolute_url()] = []
                    continue
                elif country_val == "(Rostov, Sverdlovsk, Tver) Russian Federation":
                    vl_answer.set_property('w_official-country-region', [mapping["Russian Federation"]])
                    state['updated_answers'][vl_answer.absolute_url()] = ["Russian Federation"]
                    continue
                elif country_val.strip() == "Areas of Mali Ston Bay, the mouth of the river Krka and waters of the northwestern part of the Zadar Count in Croatia":
                    vl_answer.set_property('w_official-country-region', [mapping["Croatia"]])
                    state['updated_answers'][vl_answer.absolute_url()] = ["Croatia"]
                    continue

                # dynamic
                countries = [country.strip() for country in country_val.split(',')]

                # split last 'and' instead of ','
                ending_country = countries[-1].split(' and ')
                if len(ending_country) == 2:
                    countries[-1] = ending_country[0].strip()
                    countries.append(ending_country[1].strip())

                # match and replace
                for country in countries:
                    if country in ignored:
                        continue
                    if country not in mapping:
                        state['errors'][vl_answer.absolute_url()] = 'Not matched %s' % country
                        break
                else:
                    #ignore duplicates
                    value = []
                    for country in set(countries) - ignored:
                        if isinstance(mapping[country], list):
                            for c in mapping[country]:
                                value.append(mapping[c])
                        else:
                            value.append(mapping[country])
                    vl_answer.set_property('w_official-country-region', sorted(set(value)))
                    state['updated_answers'][vl_answer.absolute_url()] = [country for country in countries]


    def _update_vl_id_in_rt(self, state):
        rt_viewer = self.aq_parent['review-template-viewer']
        for rt_shadow in rt_viewer.iter_assessments(show_drafts=True):
            target_answer = rt_shadow.target_answer()
            if rt_shadow.library_id:
                vlid = target_answer.get('w_vlid')
                if vlid:
                    state['already_updated'].append(target_answer.absolute_url())
                else:
                    setattr(target_answer, 'w_vlid', rt_shadow.library_id)
                    target_answer._p_changed = True
                    state['updated_answers'][target_answer.absolute_url()] = [rt_shadow.library_id]
            else:
                state['orphan_answers'].append(target_answer.absolute_url())



    def _update_vl_countries_and_region(self, state, review_template, library):
        def match_answers(vl_answer, rt_answer):
            vl_title_dict = vl_answer.get('w_assessment-name')
            rt_title_dict = rt_answer.get('w_q1-name-assessment-report')
            if not isinstance(vl_title_dict, dict) or not isinstance(rt_title_dict, dict):
                return False

            for vl_title in vl_title_dict.values():
                for rt_title in rt_title_dict.values():
                    if vl_title.strip() and vl_title.strip() == rt_title.strip():
                        return True
            return False

        def copy_country_and_region(vl_answer, rt_answer):
            setattr(vl_answer, 'w_official-country-region', getattr(rt_answer.aq_base, 'w_official-country-region', ''))
            setattr(vl_answer, 'w_geo-coverage-region', getattr(rt_answer.aq_base, 'w_geo-coverage-region', ''))
            vl_answer._p_changed = True

        def empty_country_and_region(vl_answer):
            setattr(vl_answer, 'w_official-country-region', '')
            setattr(vl_answer, 'w_geo-coverage-region', '')
            vl_answer._p_changed = True

        for vl_answer in library.objectValues(survey_answer_metatype):
            for rt_answer in review_template.objectValues(survey_answer_metatype):
                if match_answers(vl_answer, rt_answer):
                    copy_country_and_region(vl_answer, rt_answer)
                    state['updated_answers'][vl_answer.absolute_url()] = [rt_answer.absolute_url()]
                    break
            else:
                state['orphan_answers'].append(vl_answer.absolute_url())
                empty_country_and_region(vl_answer)


    def _update_remove_acronyms(self, state, review_template):
        localized_strings = ['w_country',
            'w_if-networked-provide-details-nature-network',
            'w_if-others-specify1353', 'w_if-others-specify1421',
            'w_if-others-specify8707', 'w_if-regional-specify-region',
            'w_if-yes-how', 'w_if-yes-list-and-provide-details',
            'w_if-yes-list-main-ones', 'w_if-yes-list-mains-ones6917',
            'w_if-yes-provide-details-how-quality-was-controlled',
            'w_if-yes-provide-details1833', 'w_if-yes-provide-details6433',
            'w_if-yes-provide-details7707', 'w_if-yes-provide-details7874',
            'w_if-yes-provide-details8215', 'w_if-yes-provide-details9388',
            'w_if-yes-specify', 'w_if-yes-specify-frequency-years',
            'w_if-yes-specify-major-priority-concerns',
            'w_if-yes-specify-names-bodyies-involved',
            'w_if-yes-specify-which-languages-it-available',
            'w_if-yes-specify2297', 'w_if-yes-specify2554',
            'w_if-yes-specify2610', 'w_if-yes-specify3390',
            'w_if-yes-specify9255', 'w_name', 'w_organisation',
            'w_q1-name-assessment-report',
            'w_q18-which-languages-main-report-assessment',
            'w_q2-name-body-conducting-assessment']
        st_strings = ['w_geo-coverage-region', 'w_hardcopy',
            'w_official-country-region', 'w_q3-publishing-year-assessment']
        strings_to_remove = [u'<acronym title="Formal efforts to assemble selected knowledge with a view toward making it publicly available in a form intended to be useful for decision-making (Mitchell and others 2006). By \u2018formal\u2019 the definition requires that the assessment should be sufficiently organised to identify components such as products, participants and issuing authority. \u2018Selected knowledge\u2019 indicates that the content has a defined scope or purpose and that not all information compiled and contributed is necessarily included in the report. The sources of knowledge may vary. While results from research and scientific knowledge predominate, assessments can supplement this with local, traditional or indigenous knowledge. Further, assessments can evaluate both existing information and research conducted expressly for the purpose. The definition also notes the importance of ensuring that assessments are in the public domain, as they may influence public debate and different types of decision-makers.">', u'</acronym>']
        for answer in review_template.objectValues('Naaya Survey Answer'):
            affected_strings = []
            for localized_string in localized_strings:
                text_values = answer.get(localized_string)
                if not isinstance(text_values, dict):
                    continue
                for k,v in text_values.items():
                    found = False
                    for st in strings_to_remove:
                        if st in v:
                            v = ''.join(v.split(st))
                            affected_strings.append(localized_string)
                            found = True
                    if found:
                        answer.set_property(localized_string, {k: v})
            for st_string in st_strings:
                text_value = answer.get(st_string)
                found = False
                for st in strings_to_remove:
                    if text_value and st in text_value:
                        text_value = ''.join(text_value.split(st))
                        affected_strings.append(st_string)
                        found = True
                if found:
                    answer.set_property(st_string, text_value)
            if affected_strings:
                state['updated_answers'][answer.absolute_url()] = self.utRemoveDuplicates(affected_strings)

    def _update_rt_titles(self, state, review_template, library):
        for answer in review_template.objectValues(survey_answer_metatype):
            vl_id = answer.get('w_vlid')
            if not vl_id:
                state['orphan_answers'].append(answer.absolute_url())
                continue

            vl_answer = getattr(library, vl_id, None)
            if vl_answer is None:
                state['errors'][vl_answer.absolute_url()] = "Specified answer id doesn't exist in the Virtual Library"
                continue
            try:
                new_title = vl_answer.get('w_assessment-name')
                old_title = answer.get('w_q1-name-assessment-report')
                if new_title['en'] != old_title['en'] or \
                    new_title['ru'] != old_title['ru']:
                    answer.set_property('w_q1-name-assessment-report', {'en': new_title['en'], 'ru': new_title['ru']})
                    state['updated_answers'][answer.absolute_url()] = []
                    break
                else:
                    state['already_updated'].append(answer.absolute_url())
            except AttributeError:
                state['errors'][vl_answer.absolute_url()] = "AttributeError"
            except:
                state['errors'][vl_answer.absolute_url()] = "Unhandled"

    def _update_vl_approval(self, state, library):
        countries = library['w_official-country-region'].getChoices()
        for answer in library.objectValues(survey_answer_metatype):
            if getattr(answer, 'approved_date', None):
                if getattr(answer, 'cf_approval_list', None):
                    state['already_updated'].append(answer.absolute_url())
                    continue
                answer.cf_approval_list = [countries[index] for index in answer.get('w_official-country-region')]
                answer._p_changed = True
                state['updated_answers'][answer.absolute_url()] = []

    security.declareProtected(view, 'viewer_view_report_html')
    def viewer_view_report_html(self, REQUEST):
        """View the report for the viewer"""
        if REQUEST.form.has_key('review_template'):
            review_template = self.aq_parent['tools']['general_template']['general-template']
            report = review_template.getSurveyTemplate().getReport('viewer')
        elif REQUEST.form.has_key('library'):
            library = self.aq_parent['tools']['virtual_library']['bibliography-details-each-assessment']
            report = library.getSurveyTemplate().getReport('viewer')
        else:
            #the function was called directly, without parameters
            return None

        if not report:
            raise NotFound('Report %s' % ('viewer',))
        if REQUEST.has_key('answer_ids'):
            answers_list = REQUEST.get('answer_ids', [])
            if isinstance(answers_list, basestring):
                answers_list = [answers_list]
            if answers_list:
                answers = [getattr(report, answer) for answer in answers_list]
                return report.questionnaire_export(report_id='viewer', REQUEST=REQUEST, answers=answers)
        else:
            return report.questionnaire_export(REQUEST=REQUEST, report_id='viewer', answers=[])
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view_management_screens, 'delete_survey_answers')
    def delete_survey_answers(self, REQUEST):
        """Delete selected items from the parent survey"""
        target_survey = self.target_survey()

        answer_ids = REQUEST.get('answer_ids', [])
        if answer_ids:
            if isinstance(answer_ids, basestring):
                answer_ids = [answer_ids]
            answer_list = [getattr(target_survey, answer_id)
                for answer_id in answer_ids]
            shadow_list = [self.wrap_answer(answer) for answer in answer_list]
            messages = ['Deleted %s - %s' %
                (shadow_ob.get('id'), shadow_ob.get('title'))
                for shadow_ob in shadow_list]
            target_survey.manage_delObjects(answer_ids)
        else:
            messages = ['No answer was selected for deletion']
        return self.index_html(shadows=list(self.iter_assessments()),
            messages=messages, filter=False)

    security.declareProtected(view, 'filter_answers_review_template')
    def filter_answers_review_template(self, REQUEST):
        """Filter answers and feed them to the index page"""
        official_country_region = REQUEST.get('official_country_region', None)
        show_unapproved = REQUEST.get('show_unapproved', None)
        if not self.checkPermissionPublishObjects():
            show_unapproved = None
        and_or = REQUEST.get('and_or')
        themes = REQUEST.get('themes', [])
        if not isinstance(themes, list):
            themes = [themes]
        topics = REQUEST.get('topics', [])
        if not isinstance(topics, list):
            topics = [topics]
        searchbox = REQUEST.get('searchbox', '')

        if not (official_country_region or themes or show_unapproved):
            shadows = list(
                    self.iter_assessments(show_unapproved=show_unapproved))
            return self.index_html(searchbox=searchbox, shadows=shadows)

        def respects_filter(shadow):
            survey_answer = self.get_survey_answer(shadow.getId())
            if official_country_region and not (official_country_region.lower()\
                    in survey_answer.get('w_official-country-region', '').lower()\
                    or official_country_region.lower() in\
                    survey_answer.get('w_geo-coverage-region', '').lower()):
                return False
            if themes:
                if and_or == 'and':
                    for theme in themes:
                        for topics_list in survey_answer.get(theme):
                            if len(topics_list) > 0:
                                break
                        else:
                            return False
                else:
                    topic_present = False
                    for theme in themes:
                        for topics_list in survey_answer.get(theme):
                            if len(topics_list) > 0:
                                topic_present = True
                                break
                        if topic_present:
                            break
                    if not topic_present:
                        return False

            if topics:
                for topic in topics:
                    theme  = topics_to_themes[topic[0]]
                    if len(survey_answer.get(theme)[int(topic[1])]) == 0:
                        return False
            return True

        shadows = filter(respects_filter,
                self.iter_assessments(show_unapproved=show_unapproved))
        return self.index_html(searchbox=searchbox, shadows=shadows,
                official_country_region=official_country_region,
                show_unapproved=show_unapproved, themes=themes, topics=topics,
                and_or=and_or)


    security.declareProtected(view, 'filter_answers_library')
    def filter_answers_library(self, REQUEST):
        """Filter answers and feed them to the index page"""
        organization = REQUEST.get('w_body-conducting-assessment', None)
        year = REQUEST.get('w_assessment-year', None)
        try:
            year = int(year)
        except ValueError:
            year = None
        official_country_region = REQUEST.get('official_country_region', None)
        and_or = REQUEST.get('and_or')
        themes = REQUEST.get('themes', [])
        if not isinstance(themes, list):
            themes = [themes]
        topics = REQUEST.get('topics', [])
        if not isinstance(topics, list):
            topics = [topics]
        searchbox = REQUEST.get('searchbox', '')

        if not (organization or year or official_country_region or themes):
            shadows = list(self.iter_assessments())
            return self.index_html(searchbox=searchbox, shadows=shadows)

        def respects_filter(shadow):
            survey_answer = self.get_survey_answer(shadow.getId())
            if organization:
                answer_organization = survey_answer.get('w_body-conducting-assessment')
                if isinstance(answer_organization, dict):
                    for ao in answer_organization.values():
                        if organization.lower() in ao.lower():
                            break
                    else:
                        return False
                else:
                    if organization.lower() not in answer_organization.lower():
                        return False
            if year:
                answer_year = survey_answer.get('w_assessment-year', '')
                if str(year) not in answer_year:
                    return False
            if official_country_region:
                survey = self.target_survey()
                countries = survey['w_official-country-region'].getChoices()
                answer_country = survey_answer.get('w_official-country-region', [])
                if answer_country is None:
                    searchable_country = ''
                else:
                    searchable_country = ', '.join(countries[c_i] for c_i in answer_country)

                regions = survey['w_geo-coverage-region'].getChoices()
                answer_region = survey_answer.get('w_geo-coverage-region', [])
                if answer_region is None:
                    searchable_region = ''
                else:
                    searchable_region = ', '.join(regions[r_i] for r_i in answer_region)
                if (official_country_region.lower() not in searchable_country.lower() and
                        official_country_region.lower() not in searchable_region.lower()):
                    return False
            if themes:
                topic_present = False
                for theme in themes:
                    answer_theme = survey_answer.get(theme)
                    if and_or == 'and':
                        if not answer_theme:
                            return False
                    else:
                        if answer_theme:
                            topic_present = True
                    theme_topics = [int(topic[1]) for topic in topics
                            if topics_to_themes[topic[0]] == theme]
                    for topic in theme_topics:
                        if topic not in answer_theme:
                            return False
                if and_or == 'or' and not topic_present:
                    return False

            return True

        shadows = filter(respects_filter, self.iter_assessments())
        return self.index_html(searchbox=searchbox, shadows=shadows,
                organization=organization, year=year,
                official_country_region=official_country_region,
                themes=themes, topics=topics, and_or=and_or)

    security.declareProtected(view, 'filter_answers_cf_vl_aggregator')
    def filter_answers_cf_vl_aggregator(self, country, theme):
        """ Filter answers for cf and vl agregator """
        def respects_filter(shadow):
            if country not in shadow.viewer_country:
                return False
            if hasattr(shadow.aq_base, 'cf_approval_list') and country not in shadow.cf_approval_list:
                return False

            shadow_document_types = [self.get_normalized_document_type(dt_i)
                                        for dt_i in shadow.document_type]
            if not shadow_document_types:
                return False

            if theme == 'Water':
                for dt_i in shadow_document_types:
                    if dt_i in self.water_document_types:
                        break
                else:
                    return False
            else: # theme == 'Green Economy'
                for dt_i in shadow_document_types:
                    if dt_i in self.ge_document_types:
                        break
                else:
                    return False

            if theme == 'Water':
                check_themes = self.water_themes
            else: # theme == 'Green Economy'
                check_themes = self.ge_themes
            if isinstance(shadow.theme, list):
                for t in shadow.theme:
                    if t in check_themes:
                        break
                else:
                    return False
            else:
                if shadow.theme not in check_themes:
                    return False

            return True
        return filter(respects_filter, self.iter_assessments())

    security.declareProtected(view, 'get_document_types_for_themes')
    def get_document_types_for_themes(self, themes):
        """ """
        themes_document_types = set()
        if 'Water' in themes:
            for dt_i in self.water_document_types:
                themes_document_types.add(self.all_document_types[dt_i])
        if 'Green Economy' in themes:
            for dt_i in self.ge_document_types:
                themes_document_types.add(self.all_document_types[dt_i])

        survey = self.target_survey()
        survey_document_types = survey['w_type-document'].getChoices()

        choices = set(survey_document_types) & themes_document_types
        return [{'index': survey_document_types.index(dt), 'value': dt}
                for dt in survey_document_types if dt in choices]

    security.declareProtected(view, 'get_normalized_document_type')
    def get_normalized_document_type(self, document_type):
        """ """
        survey = self.target_survey()
        survey_document_types = survey['w_type-document'].getChoices()

        dt_name = survey_document_types[document_type]
        return self.all_document_types.index(dt_name)

    security.declareProtected(view, 'get_library_ids')
    def get_library_ids(self):
        """
        This function is for Review Template Viewer only
        """
        return set(rt_answer.library_id for rt_answer in self.iter_assessments())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'update_locations')
    def update_locations(self, REQUEST=None):
        """Update locations of selected answers"""
        if REQUEST is None:
            return
        target_survey = self.target_survey()

        answer_ids = REQUEST.get('answer_ids', [])
        new_locations = REQUEST.get('geo_location', [])
        if answer_ids and new_locations:
            if isinstance(answer_ids, basestring):
                answer_ids = [answer_ids]
            if isinstance(new_locations, basestring):
                new_locations = [new_locations]
            locations = set(new_locations)
            geo_locations = {}
            for location in locations:
                geo_locations[location] = do_geocoding(location)
            for answer_id in answer_ids:
                target_answer = getattr(target_survey, answer_id)
                location = new_locations[answer_ids.index(answer_id)]
                geo_location = geo_locations[location]
                if geo_location:
                    setattr(target_answer, 'w_location', geo_location)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

def do_geocoding(address):
    """ """
    #if self.portal_map.current_engine == 'yahoo':
    #    coordinates = geocoding.yahoo_geocode(address)
    #elif self.portal_map.current_engine == 'google':
    coordinates = geocoding.location_geocode(address)
    if coordinates != None:
        lat, lon = coordinates
        return Geo(lat, lon, address)
    return (None)

def viewer_for_survey_answer(answer):
    catalog = answer.getSite().getCatalogTool()
    for brain in catalog(meta_type=AoALibraryViewer.meta_type):
        viewer = brain.getObject()
        survey = viewer.target_survey()
        survey_path = physical_path(survey)
        answer_path = physical_path(answer)
        if answer_path.startswith(survey_path+'/'):
            # so our answer is part of the survey targeted by `viewery
            yield viewer

@adapter(INySurveyAnswerAddEvent)
def survey_answer_created(event):
    answer = event.context
    if answer.is_draft():
        return
    try:
        for viewer in viewer_for_survey_answer(answer):
            catalog = viewer.getSite().getCatalogTool()
            shadow = viewer.wrap_answer(answer)
            catalog.catalog_object(shadow, physical_path(shadow))
    except Exception, e:
        answer.getSite().log_current_error()

@adapter(INySurveyAnswer, IObjectRemovedEvent)
def survey_answer_removed(answer, event):
    if answer.is_draft():
        return
    try:
        for viewer in viewer_for_survey_answer(answer):
            catalog = viewer.getSite().getCatalogTool()
            shadow = viewer.wrap_answer(answer)
            catalog.uncatalog_object(physical_path(shadow))
    except Exception, e:
        answer.getSite().log_current_error()


