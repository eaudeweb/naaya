from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core.utils import path_in_site

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

geo_type_map = {
    0: 'symbol825', # green economy
    1: 'symbol814', # water
    2: 'symbol851', # green economy and water
}


# the "w_theme" answer is now a list, so we can't extract a geo_type.

#def extract_geo_type(answer):
#    themes_number = answer.get('w_theme')
#
#    try:
#        return geo_type_map[themes_number]
#    except KeyError:
#        return None

public_widgets = set([
    'w_assessment-name',
    'w_assessment-upload',
    'w_assessment-url',
    'w_assessment-year',
    'w_body-conducting-assessment',
    'w_green-economy',
    'w_green-economy-topics',
    'w_information-about-data-uploader',
    'w_is-formal',
    'w_location',
    'w_main-criterion',
    'w_other-criteria',
    'w_publicly-available',
    'w_registration-form-virtual-library',
    'w_resource-efficiency-topics',
    'w_specific-scope-or-purpose',
    'w_theme',
    'w_theme-coverage',
    'w_water-related-ecosystem',
    'w_water-resource-management-topics',
    'w_water-resources-topics',
])

def extract_survey_answer_data(answer):
    all_topics = set()
    for name in [
            'w_green-economy-topics',
            'w_resource-efficiency-topics',
            'w_water-resources-topics',
            'w_water-resource-management-topics']:
        all_topics.update(extract_multipleselect(answer, name))

    attrs = {
        'id': answer.getId(),
        'title': answer.get('w_assessment-name'),
        'geo_location': answer.get('w_location'),
        'uploader': ('%s %s') % (answer.get('w_submitter-name'), answer.get('w_submitter-organisation'), ),
        #'geo_type': extract_geo_type(answer),
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

    security.declareProtected(view_management_screens, 'target_answer')
    def target_answer(self):
        return self.getSite().restrictedTraverse(self.target_path)

    security.declareProtected(view, 'render_answer')
    def render_answer(self):
        answer = self.target_answer()
        datamodel = answer.getDatamodel()
        survey_template = answer.getSurveyTemplate()

        views = []
        for widget in survey_template.getSortedWidgets():
            if widget.id not in public_widgets:
                continue
            widget_data = datamodel.get(widget.id)
            views.append(widget.render(mode='view', datamodel=widget_data))

        return '\n'.join(views)

    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/assessment_index', globals(),
                            'naaya.ew_aoa_library.shadow.index_html')

    manage_main = PageTemplateFile('zpt/assessment_manage_main', globals())

def shadow_for_answer(answer):
    attrs = extract_survey_answer_data(answer)
    return AssessmentShadow(**attrs)

#print "loaded survey data module"
