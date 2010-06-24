from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
import Globals
from zope.app.container.interfaces import (IObjectAddedEvent,
                                           IObjectRemovedEvent)
from zope import interface
from zope.component import adapter

from Products.NaayaSurvey.interfaces import INySurveyAnswer
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

        if not hasattr(self, '_v_shadow_cache') or Globals.DevelopmentMode:
            self._v_shadow_cache = {}

        # Survey answers are, in effect, immutable. So we cache them by path.
        key = '/'.join(answer.getPhysicalPath())
        try:
            obj = self._v_shadow_cache[key]
        except KeyError:
            obj = shadow.shadow_for_answer(answer)
            self._v_shadow_cache[key] = obj

        return obj.__of__(self)

    security.declareProtected(view, 'iter_assessments')
    def iter_assessments(self):
        survey = self.target_survey()
        for answer in survey.objectValues(survey_answer_metatype):
            yield self.wrap_answer(answer)

    def __getitem__(self, key):
        survey = self.target_survey()
        if key not in survey.objectIds(survey_answer_metatype):
            raise KeyError
        return self.wrap_answer(survey[key])

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

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/index', globals())

    manage_main = PageTemplateFile('zpt/manage_main', globals())

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

@adapter(INySurveyAnswer, IObjectAddedEvent)
def survey_answer_created(answer, event):
    for viewer in viewer_for_survey_answer(answer):
        catalog = viewer.getSite().getCatalogTool()
        shadow = viewer.wrap_answer(answer)
        catalog.catalog_object(shadow, physical_path(shadow))

@adapter(INySurveyAnswer, IObjectRemovedEvent)
def survey_answer_removed(answer, event):
    for viewer in viewer_for_survey_answer(answer):
        catalog = viewer.getSite().getCatalogTool()
        shadow = viewer.wrap_answer(answer)
        catalog.uncatalog_object(physical_path(shadow))
