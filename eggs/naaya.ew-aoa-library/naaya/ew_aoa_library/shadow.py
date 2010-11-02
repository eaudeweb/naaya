from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core.utils import path_in_site

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

def get_library_answer(answer):
    the_survey = getattr(answer.getSite().tools.virtual_library, 'bibliography-details-each-assessment')
    for x in the_survey.objectValues('Naaya Survey Answer'):
        if x.get('w_assessment-name') == answer.get('w_q1-name-assessment-report'):
            return x
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
    return library_answer.get('w_location')

restricted_widgets = {
    'bibliography-details-each-assessment': set([
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
        'country': answer.get('w_country-or-international-organisation'),
        'geo_type': extract_geo_type(answer),
        'description': ('<strong>%s</strong><br />'
                        '%s<br />'
                        '<a href="%s">%s</a><br />') % (
                            answer.get('w_submitter-organisation'),
                            answer.get('w_assessment-year'),
                            answer.get('w_assessment-url'),
                            answer.get('w_assessment-url'),
                       ),
        'target_path': path_in_site(answer),
        'theme': extract_multipleselect(answer, 'w_theme'),
        'topics': sorted(all_topics),
        'modification_time': answer.get('modification_time'),
    }

    if not attrs['title']:
        answer_id = attrs['id']
        prefix = 'answer_'
        if answer_id.startswith(prefix):
            answer_id = answer_id[len(prefix):]
        attrs['title'] = "Assessment %s" % answer_id

    return attrs

def extract_survey_answer_data_general_template(answer):
    all_topics = set()
    multiple_selects = [
                        'w_green-economy-topics',
                        'w_resource-efficiency-topics',
                        'w_water-resources-topics',
                        'w_water-resource-management-topics'
                        ]
    for name in multiple_selects:
        all_topics.update(extract_multipleselect(get_library_answer(answer), name))

    attrs = {
        'id': answer.getId(),
        'title': answer.get('w_q1-name-assessment-report'),
        'geo_location': general_template_extract_geo_location(answer),
        'uploader': ('%s, %s') % (answer.get('w_name'),
                                  answer.get('w_organisation'), ),
        'country': answer.get('w_country'),
        #This is commented because (now) we don't want to show review template answers on the map
        #'geo_type': extract_geo_type(get_library_answer(answer)),
        'description': ('<strong>%s</strong><br />%s<br />') %
                        (
                            answer.get('w_organisation'),
                            answer.get('w_q3-publishing-year-assessment'),
                        ),
        'target_path': path_in_site(answer),
        'theme': extract_multipleselect(get_library_answer(answer), 'w_theme'),
        'topics': sorted(all_topics),
        'modification_time': answer.get('modification_time'),
    }

    if not attrs['title']:
        answer_id = attrs['id']
        prefix = 'answer_'
        if answer_id.startswith(prefix):
            answer_id = answer_id[len(prefix):]
        attrs['title'] = "Assessment %s" % answer_id

    return attrs

class AssessmentShadow(SimpleItem):
    """ Non-persistent shadow object that describes an AoA assessment """

    manage_options = (
        {'label': 'Summary', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
    ) + SimpleItem.manage_options[1:]

    meta_type = "Naaya EW_AOA Shadow Object"

    submitted = 1
    approved = 1

    security = ClassSecurityInfo()

    def __init__(self, id, **attrs):
        self._setId(id)
        self.__dict__.update(attrs)

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

    security.declareProtected(view_management_screens, 'target_answer')
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
            if widget.id in restricted_widgets[survey_id]:
                continue
            widget_data = datamodel.get(widget.id)
            views.append(widget.render(mode='view', datamodel=widget_data))

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
            email_introduction = 'Thank you for submitting the Review Template related to the "%s" report. Our system is providing below some suggestions to improve the record:\n\n' % getattr(survey_answer, 'w_q1-name-assessment-report')
            email_body = suggestion
            email_ending = '\n\n You may edit your Review Template by following this link:\n\n %s?edit=1 \n\n Thank you again for your cooperation!' % survey_answer.absolute_url()
            email_to = str(survey_answer.w_email)
            email_from = 'no-reply@aoa.eea.europa.eu'
            email_subject = 'Suggestion for review of report %s' % getattr(survey_answer, 'w_q1-name-assessment-report')
            self.getEmailTool().sendEmail(email_introduction+email_body+email_ending, email_to, email_from, email_subject)
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'remove_suggestions')
    def remove_suggestions(self, REQUEST):
        """ Removes all suggestions from a survey answer"""
        survey_answer = self.get_survey_answer(self.getId())
        survey_answer.suggestions = []
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

def get_survey_id(answer):
    return answer.aq_parent.id

def shadow_for_answer(answer):
    attrs = extract_survey_answer_data(answer)
    shadow = AssessmentShadow(**attrs)
    # the security is hardcoded to match the one of the target object
    try:
        view_perm_roles = answer.aq_parent._View_Permission 
    except AttributeError:
        pass
    else:
        shadow._View_Permission = view_perm_roles
    return shadow

#print "loaded survey data module"
