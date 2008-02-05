#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from constants import *

manage_addNySurveyAnswer_html = PageTemplateFile('zpt/answer_manage_add', globals())
answer_add_html = PageTemplateFile('zpt/answer_add_html', globals())

def addNySurveyAnswer(self, REQUEST=None, **kwargs):
    """ """
    if REQUEST:
        kwargs.update(getattr(REQUEST, 'form', {}))
    
    id = PREFIX_NYSURVEY_ANSWER + self.utGenRandomId(6)
    country = kwargs.get('country', '')
    agency = kwargs.get('agency', '')
    title = '%s %s' % (country, agency)
    user = REQUEST.AUTHENTICATED_USER.getUserName()
    
    ob = NySurveyAnswer(id, title=title, user=user, **kwargs)
    self._setObject(id, ob)
    
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '?done=ok')

class NySurveyAnswer(SimpleItem):
    """ """
    
    meta_type = METATYPE_NYSURVEY_ANSWER
    
    manage_options = (SimpleItem.manage_options)
    
    security = ClassSecurityInfo()
    
    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'index_html')
    index_html = PageTemplateFile('zpt/answer_index_html', globals())
    
    def __init__(self, id='', title='', user='', REQUEST=None, **kwargs):
        self.id = id
        self.title = title
        self.user = user
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    #api
    def get_answer_object(self):
        return self

    def get_answer_path(self, p=0):
        return self.absolute_url(p)
    
    def get_attrs(self):
        for key in self.__dict__.keys():
            if key[0] in ['a', 'b', 'c'] and key[1].isdigit():
                yield key

InitializeClass(NySurveyAnswer)
