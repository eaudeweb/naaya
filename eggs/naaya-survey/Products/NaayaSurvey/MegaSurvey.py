import logging

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile
from App.ImageFile import ImageFile
from AccessControl.Permission import Permission

from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.managers.utils import make_id
from Products.NaayaBase.NyAccess import NyAccess
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.managers.import_export import generate_csv, generate_excel

from Products.NaayaWidgets.constants import PERMISSION_ADD_WIDGETS
from BaseSurveyTemplate import BaseSurveyTemplate
from SurveyQuestionnaire import SurveyQuestionnaire
from permissions import (PERMISSION_ADD_MEGASURVEY, PERMISSION_ADD_ANSWER,
                         PERMISSION_ADD_REPORT, PERMISSION_ADD_ATTACHMENT,
                         PERMISSION_VIEW_ANSWERS, PERMISSION_EDIT_ANSWERS,
                         PERMISSION_VIEW_REPORTS)


log = logging.getLogger(__name__)

megasurvey_add_html = NaayaPageTemplateFile('zpt/megasurvey_add', globals(),
                                            'NaayaSurvey.megasurvey_add')

def manage_addMegaSurvey(context, id='', title='', lang=None, REQUEST=None, **kwargs):
    """ """
    title = title or 'Survey'
    id = make_id(context, id=id, title=title)

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
    kwargs.setdefault('contributor', contributor)

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
    if l_referer == 'megasurvey_manage_add' or l_referer.find('megasurvey_manage_add') != -1:
        return context.manage_main(context, REQUEST, update_menu=1)
    elif l_referer == 'megasurvey_add_html':
        context.setSession('referer', context.absolute_url())
        REQUEST.RESPONSE.redirect(context.absolute_url())

class MegaSurvey(SurveyQuestionnaire, BaseSurveyTemplate):
    """ """

    meta_type = 'Naaya Mega Survey'
    meta_label = 'Survey'

    _constructors = (manage_addMegaSurvey, )

    security = ClassSecurityInfo()

    edit_access = NyAccess('edit_access', {
        PERMISSION_ADD_ANSWER: "Submit answer",
        PERMISSION_ADD_REPORT: "Create report",
        PERMISSION_ADD_ATTACHMENT: "Attach file",
        PERMISSION_VIEW_ANSWERS: "View answers",
        PERMISSION_EDIT_ANSWERS: "Edit answers",
        PERMISSION_VIEW_REPORTS: "View reports",
    })

    def __init__(self, id, **kwargs):
        """ """
        #BaseSurveyTemplate.__init__(self, id, **kwargs)
        SurveyQuestionnaire.__init__(self, id, None, **kwargs)
        self.contributor = kwargs.get('contributor')
        self.approved = 1

    def can_be_seen(self):
        """
        Indicates if the current user has access to the current folder.

        """
        return self.checkPermission(view)

    def all_meta_types(self, interfaces=None):
        """What can you put inside me?"""
        return BaseSurveyTemplate.all_meta_types(self, interfaces)

    def getSurveyTemplate(self):
        """ """
        return self

    security.declareProtected(view, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """returns all the answers in a csv file"""
        def stringify(value):
            if not isinstance(value, basestring):
                value = unicode(value)
            if isinstance(value, str):
                return unicode(value, 'utf-8')
            return value
        def all_stringify(row):
            return [stringify(value) for value in row]

        answers = self.getAnswers()
        widgets = self.getSortedWidgets()
        header = ['Respondent']
        header += [widget.title_or_id() for widget in widgets]
        rows = [answer.answer_values() for answer in answers]
        rows = [all_stringify(item) for item in rows]

        file_type = REQUEST.get('file_type', 'CSV')
        if file_type == 'CSV':
            RESPONSE.setHeader('Content-Type', 'text/csv')
            RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s.csv' % self.id)
            return generate_csv(header, rows)
        if file_type == 'Excel' and self.rstk.we_provide('Excel export'):
            RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
            RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s.xls' % self.id)
            return generate_excel(header, rows)
        else: raise ValueError('unknown file format %r' % file_type)

    #
    # Site pages
    #
    security.declareProtected(view, 'index_html')
    def index_html(self):
        """ """
        if not self.checkPermissionSkipCaptcha() and not self.recaptcha_is_present():
            raise ValueError("Invalid recaptcha keys")
        return self._index_html()

    _index_html = NaayaPageTemplateFile('zpt/megasurvey_index',
                     globals(), 'NaayaSurvey.megasurvey_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = NaayaPageTemplateFile('zpt/megasurvey_edit',
                    globals(), 'NaayaSurvey.megasurvey_edit')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_attachments_html')
    edit_attachments_html = NaayaPageTemplateFile('zpt/megasurvey_edit_attachments',
                        globals(), 'NaayaSurvey.megasurvey_edit_attachments')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_questions_html')
    edit_questions_html = NaayaPageTemplateFile('zpt/megasurvey_edit_questions',
                        globals(), 'NaayaSurvey.megasurvey_edit_questions')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_reports_html')
    edit_reports_html = NaayaPageTemplateFile('zpt/megasurvey_edit_reports',
                        globals(), 'NaayaSurvey.megasurvey_edit_reports')

    #
    # change the security of the inherited methods
    #
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addWidget')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'deleteItems')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'setSortOrder')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addReport')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'generateFullReport')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'addAttachment')

    # static files
    css_survey_common = DTMLFile('www/survey_common.css', globals())
    fancy_checkmark = ImageFile('www/fancy_checkmark.gif', globals())
    survey_js = ImageFile('www/survey.js', globals())

    security.declareProtected(PERMISSION_EDIT_ANSWERS, 'bogus')
    def bogus(self):
        """ Needed in Naaya Access. It is mandatory that a permission must be
        declared so it can be used in Naaya Access.
        This should be removed once this issue is solved

        """
        pass

    security.declarePublic('display_admin_warning')
    def display_admin_warning(self):
        return self.checkPermissionPublishObjects()\
                and self.anonymous_has_access()\
                and not self.recaptcha_is_present()\
                and not self.anonymous_skips_captcha()

    security.declarePublic('anonymous_has_access')
    def anonymous_has_access(self):
        return 'Anonymous' in self.edit_access.getPermissionMapping()['Naaya - Add Naaya Survey Answer']

    security.declarePublic('anonymous_skips_captcha')
    def anonymous_skips_captcha(self):
        permission = 'Naaya - Skip Captcha'
        permission_object = Permission(permission, (), self)
        return 'Anonymous' in permission_object.getRoles()

    security.declarePrivate('dont_inherit_view_permission')
    def dont_inherit_view_permission(self):
        permission = Permission(view, (), self)
        roles = permission.getRoles()
        roles = tuple(set(roles) | set(['Manager', 'Administrator', 'Owner']))
        permission.setRoles(roles)

    security.declarePrivate('inherit_view_permission')
    def inherit_view_permission(self):
        permission = Permission(view, (), self)
        roles = permission.getRoles()
        roles = list(roles)
        permission.setRoles(roles)

InitializeClass(MegaSurvey)

def get_content_type_config():
    return {
        'meta_type': MegaSurvey.meta_type,
        'label': u"Survey",
        'folder_constructors': [
            ('megasurvey_add_html', megasurvey_add_html),
            ('manage_addMegaSurvey', manage_addMegaSurvey),
        ],
        'permission': PERMISSION_ADD_MEGASURVEY,
        'add_form': 'megasurvey_add_html',
    }

def install_permissions(site):
    """
    Configure security for surveys:
        - Manager + Administrator: add/manage survey templates
        - Contributor: add/manage questionnaires (surveys)
        - Anonymous + Authenticated: add answer (take survey) & view reports
    """
    log.info('Configuring security for surveys on site %r', site)

    site.manage_permission(PERMISSION_ADD_ATTACHMENT, ('Manager', 'Administrator'), acquire=0)
    site.manage_permission(PERMISSION_ADD_WIDGETS, ('Manager', 'Administrator'), acquire=0)
    site.manage_permission(PERMISSION_ADD_REPORT, ('Manager', 'Administrator'), acquire=0)
    site.manage_permission(PERMISSION_ADD_MEGASURVEY, ('Manager', 'Administrator', 'Contributor', ), acquire=0)
    site.manage_permission(PERMISSION_ADD_ANSWER, ('Anonymous', ), acquire=0)
    site.manage_permission(PERMISSION_VIEW_REPORTS, ('Anonymous', ), acquire=0)
    site.manage_permission(PERMISSION_VIEW_ANSWERS, ('Manager', 'Administrator', 'Contributor', 'Owner'), acquire=0)
    site.manage_permission(PERMISSION_EDIT_ANSWERS, ('Manager', 'Administrator', ), acquire=0)

def install_catalog_index(site):
    """Configure catalog tool:
        - add a survey_template index for the getSurveyTemplateId method
    """
    catalog_tool = site.getCatalogTool()
    log.info('Configuring catalog tool %r', catalog_tool)
    if 'respondent' not in catalog_tool.indexes():
        catalog_tool.addIndex('respondent', 'FieldIndex')

def pluggable_item_installed_in_site(evt):
    if evt.meta_type != MegaSurvey.meta_type:
        return # some other content type that we don't care about
    site = evt.context
    install_permissions(site)
