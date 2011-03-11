from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
import Globals
from zope.app.container.interfaces import (IObjectAddedEvent,
                                           IObjectRemovedEvent)
from zope import interface
from zope.component import adapter
from ZPublisher import NotFound

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaSurvey.interfaces import INySurveyAnswer, INySurveyAnswerAddEvent
from Products.NaayaCore.CatalogTool.interfaces import INyCatalogAware

import shadow

survey_answer_metatype = 'Naaya Survey Answer'

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

class AoALibraryViewer(SimpleItem):
    interface.implements(INyCatalogAware)

    meta_type = "Naaya EW_AOA Library Viewer"

    manage_options = (
        {'label': 'Summary', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
        {'label':'Updates', 'action':'manage_update_html'},
    ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, target_path):
        self._setId(id)
        self.title = title
        self.target_path = target_path

    security.declareProtected(view_management_screens, 'target_survey')
    def target_survey(self):
        return self.getSite().restrictedTraverse(self.target_path)

    security.declarePrivate('wrap_answer')
    def wrap_answer(self, answer):
        if Globals.DevelopmentMode:
            reload(shadow)

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
    def iter_assessments(self, show_unapproved=True):
        survey = self.target_survey()
        for answer in survey.objectValues(survey_answer_metatype):
            if answer.is_draft():
                continue
            if not hasattr(answer, 'approved_date') and not show_unapproved:
                continue
            yield self.wrap_answer(answer)

    def __getitem__(self, key):
        survey = self.target_survey()
        if key not in survey.objectIds(survey_answer_metatype):
            raise KeyError
        if survey[key].is_draft():
            raise KeyError
        return self.wrap_answer(survey[key])

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
    def index_html(self, **kwargs):
        """ """
        filter = True
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
        updated_answers = []
        errors = {}
        orphan_answers = []
        review_template = self.aq_parent['tools']['general_template']['general-template']
        library = self.aq_parent['tools']['virtual_library']['bibliography-details-each-assessment']
        for answer in review_template.objectValues(survey_answer_metatype):
            title_dict = answer.get('w_q1-name-assessment-report')
            if not title_dict:
                orphan_answers.append(answer.absolute_url())
                continue
            temp_title = title_dict['en']
            if not temp_title:
                temp_title = title_dict['ru']
            for vl_answer in library.objectValues(survey_answer_metatype):
                try:
                    vl_answers = [vl_title.strip() for vl_title in vl_answer.get('w_assessment-name').values()]
                    if  temp_title.strip() in vl_answers:
                        new_title = vl_answer.get('w_assessment-name')
                        answer.set_property('w_q1-name-assessment-report', {'en': new_title['en'], 'ru': new_title['ru']})
                        updated_answers.append(answer.absolute_url())
                        break
                except AttributeError:
                    errors[vl_answer.absolute_url()] = "AttributeError"
                except:
                    errors[vl_answer.absolute_url()] = "Unhandled"
            else:
                orphan_answers.append(answer.absolute_url())
        return self._manage_update_html(updated_answers=updated_answers,
            errors=errors.items(), orphan_answers=orphan_answers)

    _manage_update_html = PageTemplateFile('zpt/viewer_manage_update', globals())

    security.declareProtected(view, 'viewer_view_report_html')
    def viewer_view_report_html(self, REQUEST):
        """View the report for the viewer"""
        review_template = self.aq_parent['tools']['general_template']['general-template']
        report = review_template.getSurveyTemplate().getReport('viewer')
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

    security.declareProtected(view, 'filter_answers')
    def filter_answers(self, REQUEST):
        """Filter answers and feed them to the index page"""
        official_country_region = REQUEST.get('official_country_region', None)
        show_unapproved = REQUEST.get('show_unapproved', None)
        if not self.checkPermissionPublishObjects():
            show_unapproved = None
        themes = REQUEST.get('themes', [])
        if isinstance(themes, basestring):
            themes = [themes]
        if not (official_country_region or themes or show_unapproved):
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        shadows = []
        for shadow in list(self.iter_assessments(show_unapproved=show_unapproved)):
            survey_answer = self.get_survey_answer(shadow.getId())
            if official_country_region and not (official_country_region.lower() in
                    getattr(survey_answer.aq_base, 'w_official-country-region', '').lower()
                    or official_country_region.lower() in
                    getattr(survey_answer.aq_base, 'w_geo-coverage-region', '').lower()):
                continue
            if themes:
                for theme in themes:
                    if not hasattr(survey_answer.aq_base, theme):
                        #If the answer doesn't have the searched attribute
                        #break the first for and go to next shadow
                        break
                    for topic in getattr(survey_answer.aq_base, theme):
                        if len(topic) > 0:
                            #If the current topic is not an empty list
                            #break the second for and go to next theme in themes
                            break
                    else:
                        #If the attribute is a list of empty lists
                        #break the first for and go to next shadow
                        break
                else:
                    shadows.append(shadow)
            else:
                #If no themes are selected, just append the shadow to the list
                shadows.append(shadow)
        return self.index_html(shadows=shadows, official_country_region=official_country_region, show_unapproved=show_unapproved, themes=themes)

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
