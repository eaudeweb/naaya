# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from DateTime import DateTime
from Globals import InitializeClass

# Product imports
from Products.NaayaCore.managers.utils import utils

from SurveyTemplate import SurveyTemplate
from SurveyQuestionnaire import SurveyQuestionnaire

def manage_addMegaSurvey(context, id='', title='', lang=None, REQUEST=None, **kwargs):
    """ """
    util = utils()
    if not title:
        title = 'Mega Survey'
    if not id:
        id = util.utGenObjectId(title)

    idSuffix = ''
    while id+idSuffix in context.objectIds():
        idSuffix = util.utGenRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = REQUEST and REQUEST.form.get('lang', None)
    lang = lang or kwargs.get('lang', context.gl_get_selected_language())

    if REQUEST:
        kwargs.update(REQUEST.form)
    kwargs['releasedate'] = context.process_releasedate(kwargs.get('releasedate', DateTime()))
    kwargs['expirationdate'] = context.process_releasedate(kwargs.get('expirationdate', DateTime()))
    contributor = context.REQUEST.AUTHENTICATED_USER.getUserName()
    #log post date
    auth_tool = context.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)

    kwargs.setdefault('id', id)
    kwargs.setdefault('title', title)
    kwargs.setdefault('lang', lang)

    ob = MegaSurvey(**kwargs)
    context.gl_add_languages(ob)
    context._setObject(id, ob)

    ob = context._getOb(id)
    ob.updatePropertiesFromGlossary(lang)
    ob.submitThis()
    context.recatalogNyObject(ob)

    # Return
    if not REQUEST:
        return id
    #redirect if case
    if REQUEST.has_key('submitted'): ob.submitThis()
    l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if l_referer == 'questionnaire_manage_add' or l_referer.find('questionnaire_manage_add') != -1:
        return context.manage_main(context, REQUEST, update_menu=1)
    elif l_referer == 'questionnaire_add_html':
        context.setSession('referer', context.absolute_url())
        REQUEST.RESPONSE.redirect('%s/messages_html' % context.absolute_url())



class MegaSurvey(SurveyTemplate, SurveyQuestionnaire):
    """ """

    meta_type = 'Naaya Mega Survey'
    meta_label = 'Mega Survey'

    _constructors = (manage_addMegaSurvey, )

    security = ClassSecurityInfo()

    def __init__(self, id, **kwargs):
        """ """
        SurveyTemplate.__init__(self, id, **kwargs)
        SurveyQuestionnaire.__init__(self, id, None, **kwargs)

    security.declareProtected(view, 'getSurveyTemplate')
    def getSurveyTemplate(self):
        """Return the survey template used for this questionnaire"""
        return self

    security.declareProtected(view, 'getSurveyTemplateId')
    def getSurveyTemplateId(self):
        """Return survey template id; used by the catalog tool."""
        return None

InitializeClass(MegaSurvey)
