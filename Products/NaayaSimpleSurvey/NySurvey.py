#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from constants import *
from NySurveyTemplate import manage_addNySurveyTemplate_html, addNySurveyTemplate

manage_addNySurvey_html = PageTemplateFile('zpt/survey_manage_add', globals())

def addNySurvey(self, id='', title='', date='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYSURVEY + self.utGenRandomId(6)
    ob = NySurvey(id, title, date)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NySurvey(Folder):
    """ """
    
    meta_type = METATYPE_NYSURVEY
    
    manage_options = (Folder.manage_options)
    
    meta_types = ({'name':METATYPE_NYSURVEY_TEMPLATE, 'action':'manage_addNySurveyTemplate_html'}, )
    
    security = ClassSecurityInfo()
    
    all_meta_types = meta_types
    
    security.declareProtected(PERMISSION_NYSURVEY_RESPOND, 'index_html')
    index_html = PageTemplateFile('zpt/survey_index_html', globals())
    
    #constructors
    manage_addNySurveyTemplate_html = manage_addNySurveyTemplate_html
    addNySurveyTemplate = addNySurveyTemplate
    
    #manage all templates
    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_templates')
    manage_templates = PageTemplateFile('zpt/manage_templates_html', globals())

    def __init__(self, id='', title='', date=''):
        
        self.id = id
        self.title = title
        self.date = date

    def get_survey_object(self):
        return self

    def get_survey_path(self, p=0):
        return self.absolute_url(p)

    def get_survey_templates(self):
        return self.objectValues(METATYPE_NYSURVEY_TEMPLATE)

    def count_templates(self):
        return len(self.objectValues(METATYPE_NYSURVEY_TEMPLATE))

InitializeClass(NySurvey)