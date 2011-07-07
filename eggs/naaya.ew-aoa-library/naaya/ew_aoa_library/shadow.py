from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.Localizer.LocalPropertyManager import LocalPropertyManager
from naaya.core.zope2util import path_in_site

PERMISSION_PUBLISH_OBJECTS = 'Naaya - Publish content'

def extract_checkboxmatrix(answer, widget_name):
    widget = answer.getSurveyTemplate()[widget_name]
    datamodel = answer.get(widget_name)
    if datamodel is None:
        return

    for index, row_answers in enumerate(datamodel):
        if row_answers:
            row_answer_names = tuple(widget.choices[answer]
                                     for answer in row_answers)
            yield (widget.rows[index], row_answer_names)

def extract_multipleselect(answer, widget_name):
    if answer is None:
        return []
    widget = answer.getSurveyTemplate()[widget_name]
    datamodel = answer.get(widget_name)
    if datamodel is None:
        return []
    else:
        return [widget.choices[n] for n in datamodel]

def extract_singleselect(answer, widget_name):
    widget = answer.getSurveyTemplate()[widget_name]
    datamodel = answer.get(widget_name)
    if datamodel is None:
        return None
    else:
        return widget.choices[datamodel]

def get_library_survey_info(site):
    if hasattr(get_library_survey_info, 'cache'):
        return get_library_survey_info.cache

    survey = getattr(site.tools.virtual_library, 'bibliography-details-each-assessment')
    answers = survey.objectValues('Naaya Survey Answer')

    answer_values = {}
    for a in answers:
        a_value = a.get('w_assessment-name')
        if isinstance(a_value, dict):
            answer_values[a.id] = a_value.values()
        else:
            answer_values[a.id] = [a_value]

    get_library_survey_info.cache = answer_values

    return get_library_survey_info.cache

def get_library_answer(answer):
    #First look for the saved parent id
    #and if that answer still exists in the library, return it
    survey = getattr(answer.getSite().tools.virtual_library, 'bibliography-details-each-assessment')
    saved_parent_id = answer.get('w_vlid')
    if saved_parent_id and hasattr(survey, saved_parent_id):
        return(survey._getOb(saved_parent_id))

    #if not, try it the old way, comparing titles
    survey_info = get_library_survey_info(answer.getSite())
    answer_value = answer.get('w_q1-name-assessment-report')
    if isinstance(answer_value, dict):
        answer_values = answer_value.values()
    else:
        answer_values = [answer_value]
    for x_id, x_values in survey_info.items():
        for xv in x_values:
            if xv and xv in answer_values:
                return survey._getOb(x_id)

    return None

geo_type = {
    'Green': 'symbol825', # green economy
    'Water': 'symbol814', # water
    'Green and water': 'symbol851', # green economy and water
}

theme = {
    'Green economy': 0, # green economy
    'Water resources': 1, # water
    'Water resource management': 2, # green economy and water
    'Resource efficiency': 3, # green economy and water
}

# the "w_theme" answer is now a list, so the assignment of a geo_type changes:
def extract_geo_type(answer):
    ''' returns a value if green and water, another value if green without water,
    a third if water (--> without green), or None if somehow the themes_list is empty'''
    themes_list = answer.get('w_theme')
    if theme['Green economy'] in themes_list or theme['Resource efficiency'] in themes_list:
        if theme['Water resources'] in themes_list or theme['Water resource management'] in themes_list:
            return geo_type['Green and water']
        else:
            return geo_type['Green']
    if theme['Water resources'] in themes_list or theme['Water resource management'] in themes_list:
        return geo_type['Water']
    return None

def general_template_extract_geo_location(answer):
    ''' returns the geo_location of the corresponding answer from the virtual library '''
    library_answer = get_library_answer(answer)
    try:
        return library_answer.get('w_location')
    except:
        pass

restricted_widgets = {
    'bibliography-details-each-assessment': set([
        'w_information-about-data-uploader',
        'w_submitter-name',
        'w_submitter-email',
        'w_submitter-organisation',
        ]),
    'bibliography-assessments-geo-5': set([
        'w_information-about-data-uploader',
        'w_submitter-name',
        'w_submitter-email',
        'w_submitter-organisation',
        ]),
    'general-template': set([
            'w_part-10-information-about-data-uploader',
            'w_name',
            'w_email',
            'w_organisation',
        ]),
}

def extract_survey_answer_data(answer):
    mapping = {'bibliography-details-each-assessment':
                    extract_survey_answer_data_library,
               'bibliography-assessments-geo-5':
                    extract_survey_answer_data_library,
               'country_fiches':
                    extract_survey_answer_data_country_fiches,
               'general-template':
                    extract_survey_answer_data_general_template}

    survey_id = get_survey_id(answer)
    assert survey_id in mapping.keys()

    func = mapping[survey_id]
    return func(answer)

def extract_survey_answer_data_library(answer):
    all_topics = set()
    multiple_selects = [
                        'w_green-economy-topics',
                        'w_resource-efficiency-topics',
                        'w_water-resources-topics',
                        'w_water-resource-management-topics'
                        ]
    for name in multiple_selects:
        all_topics.update(extract_multipleselect(answer, name))

    attrs = {
        'id': answer.getId(),
        'title': answer.get('w_assessment-name'),
        'geo_location': answer.get('w_location'),
        'uploader': ('%s, %s') % (answer.get('w_submitter-name'),
                                  answer.get('w_submitter-organisation'), ),
        'country': answer.get(key='w_country-or-international-organisation', default=''),
        'geo_type': extract_geo_type(answer),
        'description': ('<strong>%s</strong><br />'
                        '%s<br />'
                        '<a href="%s">%s</a><br />') % (
                            answer.get('w_submitter-organisation'),
                            answer.get('w_assessment-year'),
                            answer.get('w_assessment-url'),
                            answer.get('w_assessment-url'),
                       ),
        'publication_year': answer.get('w_assessment-year'),
        'target_path': path_in_site(answer),
        'theme': extract_multipleselect(answer, 'w_theme'),
        'topics': sorted(all_topics),
        'modification_time': answer.modification_time,
    }

    if not attrs['title']:
        answer_id = attrs['id']
        prefix = 'answer_'
        if answer_id.startswith(prefix):
            answer_id = answer_id[len(prefix):]
        attrs['title'] = "Assessment %s" % answer_id

    attrs['geo_coverage_country'] = getattr(answer.aq_base, 'w_official-country-region', [])

    attrs['geo_coverage_region'] = getattr(answer.aq_base, 'w_geo-coverage-region', '')

    attrs['document_type'] = getattr(answer.aq_base, 'w_type-document', 0)

    return attrs

def extract_survey_answer_data_country_fiches(answer):
    attrs =  {
            'id': answer.getId(),
            'title': answer.get('w_title'),
            'geo_coverage_country': answer.get('w_country'),
            'publication_year': answer.get('w_publication-year'),
            'uploader': answer.get('w_author'),
            'target_path': path_in_site(answer),
            'theme': extract_multipleselect(answer, 'w_theme'),
            'modification_time': answer.modification_time,
            }

    attrs['document_type'] = getattr(answer.aq_base, 'w_type-document')

    return attrs

def extract_survey_answer_data_general_template(answer):
    library_answer = get_library_answer(answer)
    if library_answer:
        library_id = library_answer.getId()
    else:
        library_id = None

    all_topics = set()
    multiple_selects = [
                        'w_green-economy-topics',
                        'w_resource-efficiency-topics',
                        'w_water-resources-topics',
                        'w_water-resource-management-topics'
                        ]
    for name in multiple_selects:
        all_topics.update(extract_multipleselect(library_answer, name))
    uploader = {}
    for language in answer.gl_get_languages():
        uploader[language] = ', '.join(filter(None, [answer.get(key='w_name', lang=language), answer.get(key='w_organisation', lang=language)]))
    if library_answer:
        publication_year = library_answer.get('w_assessment-year')
    else:
        publication_year = answer.get('w_q3-publishing-year-assessment')\
            or answer.get('w_hardcopy')
    if publication_year:
        publication_year = 'Year: %s' % publication_year
    attrs = {
        'id': answer.getId(),
        'title': answer.get('w_q1-name-assessment-report'),
        'geo_location': general_template_extract_geo_location(answer),
        'library_id': library_id,
        'uploader': uploader,
        'country': answer.get(key='w_country', default=''),
        #This is commented because (now) we don't want to show review template answers on the map
        #'geo_type': extract_geo_type(library_answer),
        'description': ('<strong>%s</strong><br />%s<br />') %
                        (
                            answer.get('w_organisation'),
                            answer.get('w_q3-publishing-year-assessment'),
                        ),
        'target_path': path_in_site(answer),
        'theme': extract_multipleselect(library_answer, 'w_theme'),
        'topics': sorted(all_topics),
        'publication_year': publication_year,
        'modification_time': answer.modification_time,
    }

    if not attrs['title']:
        answer_id = attrs['id']
        prefix = 'answer_'
        if answer_id.startswith(prefix):
            answer_id = answer_id[len(prefix):]
        attrs['title'] = "Assessment %s" % answer_id

    attrs['geo_coverage_country'] = getattr(answer.aq_base, 'w_official-country-region', '')

    attrs['geo_coverage_region'] = getattr(answer.aq_base, 'w_geo-coverage-region', '')
    if library_answer:
        attrs['library_geo_coverage_country'] = getattr(library_answer.aq_base, 'w_official-country-region', '')
        attrs['library_geo_coverage_region'] = getattr(library_answer.aq_base, 'w_geo-coverage-region', '')
    else:
        attrs['library_geo_coverage_country'] = None
        attrs['library_geo_coverage_region'] = None

    return attrs

class AssessmentShadow(SimpleItem, LocalPropertyManager):
    """ Non-persistent shadow object that describes an AoA assessment """

    manage_options = (
        {'label': 'Summary', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
        {'label': 'Updates', 'action':'manage_updates_html'},
    ) + SimpleItem.manage_options[1:]

    meta_type = "Naaya EW_AOA Shadow Object"

    submitted = 1
    approved = 1

    security = ClassSecurityInfo()

    def __init__(self, id, **attrs):
        self._setId(id)
        for key, value in attrs.items():
            if isinstance(value, dict):
                self._setLocalProperty(key, 'string')
                for lang, lang_value in value.items():
                    self._setLocalPropValue(key, lang, lang_value)
            else:
                setattr(self, key, value)

    def get(self, key):
        if self.hasLocalProperty(key):
            lang = self.gl_get_selected_language()
            value = self.getLocalProperty(key, lang=lang)
            if value:
                return value

            # try other languages for non-empty value
            for lang in self.gl_get_languages():
                value = self.getLocalProperty(key, lang=lang)
                if value:
                    return '%s: %s' % (lang, value)

        return getattr(self, key)

    def geo_latitude(self):
        if self.geo_location is None:
            raise AttributeError
        if self.geo_location.lat is None:
            raise AttributeError
        return self.geo_location.lat

    def geo_longitude(self):
        if self.geo_location is None:
            raise AttributeError
        if self.geo_location.lon is None:
            raise AttributeError
        return self.geo_location.lon

    security.declareProtected(view_management_screens, 'set_geo_location')
    def set_geo_location(self, lat, lon):
        ''' set lat and lon properties to the Geo object (if missing...)'''
        from Products.NaayaCore.SchemaTool.widgets.geo import Geo
        target_answer = self.target_answer()
        current_address = target_answer.w_location.address
        target_answer.w_location = Geo(lat=lat, lon=lon, address=current_address)

    security.declareProtected(view, 'target_answer')
    def target_answer(self):
        return self.getSite().restrictedTraverse(self.target_path)

    security.declareProtected(view, 'render_answer')
    def render_answer(self):
        answer = self.target_answer()
        survey_id = get_survey_id(answer)
        datamodel = answer.getDatamodel()
        survey_template = answer.getSurveyTemplate()

        views = []
        for widget in survey_template.getSortedWidgets():
            if not self.checkPermission(PERMISSION_PUBLISH_OBJECTS):
                if widget.id in restricted_widgets[survey_id]:
                    continue
            widget_data = datamodel.get(widget.id)
            views.append(widget.render(mode='view', datamodel=widget_data, parent=answer))

        return '\n'.join(views)

    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/assessment_index', globals(),
                            'naaya.ew_aoa_library.shadow.index_html')

    manage_main = PageTemplateFile('zpt/assessment_manage_main', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'suggestions')
    def suggestions(self):
        survey_answer = self.get_survey_answer(self.getId())
        return getattr(survey_answer, 'suggestions', [])

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'add_suggestion')
    def add_suggestion(self, suggestion, REQUEST):
        """ Adds a suggestion to the survey answer"""
        survey_answer = self.get_survey_answer(self.getId())
        if suggestion:
            if hasattr(survey_answer, 'suggestions'):
                survey_answer.suggestions.append(suggestion)
            else:
                survey_answer.suggestions = [suggestion]
            survey_answer._p_changed = True
            #email_introduction = 'Thank you for submitting the Review Template related to the "%s" report. Our system is providing below some suggestions to improve the record:\n\n' % getattr(survey_answer, 'w_q1-name-assessment-report')
            email_body = '%s \n\n %s?edit=1' % (suggestion, survey_answer.absolute_url())
            #email_ending = '\n\n You may edit your Review Template by following this link:\n\n %s?edit=1 \n\n Thank you again for your cooperation!' % survey_answer.absolute_url()
            email_to = str(survey_answer.w_email)
            email_from = self.getSite().mail_address_from
            email_subject = 'Suggestion for review of report %s' % self.get('title')
            self.getEmailTool().sendEmail(email_body, email_to, email_from, email_subject)
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'remove_suggestions')
    def remove_suggestions(self, REQUEST):
        """ Removes all suggestions from a survey answer"""
        survey_answer = self.get_survey_answer(self.getId())
        survey_answer.suggestions = []
        survey_answer._p_changed = True
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'set_region')
    def set_region(self, REQUEST):
        """ Saves the official country/region"""
        survey_answer = self.get_survey_answer(self.getId())
        setattr(survey_answer, 'w_official-country-region', REQUEST.get('geo_coverage_country'))
        setattr(survey_answer, 'w_geo-coverage-region', REQUEST.get('geo_coverage_region'))
        survey_answer._p_changed = True
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'save_vl')
    def save_vl(self, REQUEST):
        """ Saves country/region and document type for VL"""
        survey_answer = self.get_survey_answer(self.getId())

        document_type = REQUEST.get('document_type')
        if document_type == 0:
            if hasattr(survey_answer.aq_base, 'w_type-document'):
                delattr(survey_answer, 'w_type-document')
        else:
            setattr(survey_answer, 'w_type-document', document_type)

        setattr(survey_answer, 'w_official-country-region', REQUEST.get('geo_coverage_country'))
        setattr(survey_answer, 'w_geo-coverage-region', REQUEST.get('geo_coverage_region'))
        survey_answer._p_changed = True
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'approve_assessment')
    def approve_assessment(self, REQUEST):
        """ Approve an assessment """
        survey_answer = self.get_survey_answer(self.getId())
        survey_answer.approved_date = DateTime()
        survey_answer._p_changed = True
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'unapprove_assessment')
    def unapprove_assessment(self, REQUEST):
        """ Unapprove an assessment """
        survey_answer = self.get_survey_answer(self.getId())
        survey_answer.approved_date = None
        survey_answer._p_changed = True
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view_management_screens, 'manage_updates_html')
    def manage_updates_html(self, REQUEST=None):
        """ Update answer report title"""

        errors = []
        the_answer = self.target_answer()
        if REQUEST.form.has_key('new_title'):
            new_title = REQUEST.get('new_title')
            language = REQUEST.get('language')
            languages = ['en', 'ru']

            if not new_title:
                errors.append('No new title provided')
            if not language:
                errors.append('No language provided')
            elif language not in languages:
                errors.append('Invalid language code')

            if not errors:
                languages.remove(language)
                try:
                    the_answer.set_property('w_q1-name-assessment-report', {language: new_title, languages[0]:''})
                except AttributeError:
                    try:
                        the_answer.set_property('w_assessment-name', {language: new_title, languages[0]:''})
                    except AttributeError:
                        errors.append('Requested field not present in the target answer')
            if errors:
                return self._manage_updates_html(errors=errors)
            return self._manage_updates_html(title_success=True)

        elif REQUEST.form.has_key('new_respondent'):
            new_respondent =  REQUEST.get('new_respondent')
            if not new_respondent:
                errors.append('No new respondent provided')
                return self._manage_updates_html(errors=errors)
            if not errors:
                setattr(the_answer, 'respondent', new_respondent)
                return self._manage_updates_html(respondent_success=True)
        else:
            return self._manage_updates_html()

    _manage_updates_html = PageTemplateFile('zpt/shadow_manage_update', globals())

def get_survey_id(answer):
    return answer.aq_parent.id

def shadow_for_answer(answer):
    attrs = extract_survey_answer_data(answer)
    shadow = AssessmentShadow(**attrs)
    # the security is hardcoded to match the one of the target object
    try:
        view_perm_roles = ('Anonymous', 'Authenticated',)
    except AttributeError:
        pass
    else:
        shadow._View_Permission = view_perm_roles
    return shadow

#print "loaded survey data module"
