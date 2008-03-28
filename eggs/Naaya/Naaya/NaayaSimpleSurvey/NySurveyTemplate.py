#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from constants import *
from NySurveyAnswer import manage_addNySurveyAnswer_html, addNySurveyAnswer, answer_add_html

manage_addNySurveyTemplate_html = PageTemplateFile('zpt/template_manage_add', globals())

def addNySurveyTemplate(self, id='', title='',date='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYSURVEY_TEMPLATE + self.utGenRandomId(6)
    ob = NySurveyTemplate(id, title, date)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NySurveyTemplate(Folder):
    """ """

    meta_type = METATYPE_NYSURVEY_TEMPLATE

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    security = ClassSecurityInfo()

    meta_types = ({'name':METATYPE_NYSURVEY_ANSWER, 'action':'manage_addNySurveyAnswer_html'}, )
    all_meta_types = meta_types

    security.declareProtected(PERMISSION_NYSURVEY_RESPOND, 'index_html')
    index_html = PageTemplateFile('zpt/template_index_html', globals())

    security.declareProtected(PERMISSION_NYSURVEY_RESPOND, 'answer_end')
    answer_end = PageTemplateFile('zpt/answer_end_html', globals())

    #constructors
    manage_addNySurveyAnswer_html = manage_addNySurveyAnswer_html

    security.declareProtected(PERMISSION_NYSURVEY_RESPOND, 'addNySurveyAnswer')
    def addNySurveyAnswer(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)

        for k, v in kwargs.items():
            REQUEST.SESSION.set(k, v)

        if not kwargs.has_key('a113'): kwargs['a113'] = ''
        if not kwargs.has_key('a114'): kwargs['a114'] = ''
        if not kwargs.has_key('a115'): kwargs['a115'] = ''
        if not kwargs.has_key('a123'): kwargs['a123'] = ''
        if not kwargs.has_key('a131'): kwargs['a131'] = ''
        if not kwargs.has_key('a211'): kwargs['a211'] = ''
        if not kwargs.has_key('a212'): kwargs['a212'] = ''
        if not kwargs.has_key('a213'): kwargs['a213'] = ''
        if not kwargs.has_key('a214'): kwargs['a214'] = ''
        if not kwargs.has_key('a217'): kwargs['a217'] = ''
        if not kwargs.has_key('a218'): kwargs['a218'] = ''
        if not kwargs.has_key('a219'): kwargs['a219'] = ''
        if not kwargs.has_key('a221'): kwargs['a221'] = ''
        if not kwargs.has_key('a222'): kwargs['a222'] = ''
        if not kwargs.has_key('a231'): kwargs['a231'] = ''
        if not kwargs.has_key('a241'): kwargs['a241'] = ''
        if not kwargs.has_key('a242'): kwargs['a242'] = ''
        if not kwargs.has_key('a243'): kwargs['a243'] = ''
        if not kwargs.has_key('a244'): kwargs['a244'] = ''
        if not kwargs.has_key('a251'): kwargs['a251'] = ''
        if not kwargs.has_key('a252'): kwargs['a252'] = ''
        if not kwargs.has_key('a311'): kwargs['a311'] = ''
        if not kwargs.has_key('a312'): kwargs['a312'] = ''
        if not kwargs.has_key('a314'): kwargs['a314'] = ''
        if not kwargs.has_key('a315'): kwargs['a315'] = ''
        if not kwargs.has_key('a321'): kwargs['a321'] = ''
        if not kwargs.has_key('a322'): kwargs['a322'] = ''
        if not kwargs.has_key('a323'): kwargs['a323'] = ''
        if not kwargs.has_key('a324'): kwargs['a324'] = ''
        if not kwargs.has_key('a352'): kwargs['a352'] = ''
        if not kwargs.has_key('a411'): kwargs['a411'] = ''
        if not kwargs.has_key('a414'): kwargs['a414'] = ''
        if not kwargs.has_key('a412'): kwargs['a412'] = ''
        if not kwargs.has_key('a431'): kwargs['a431'] = ''
        if not kwargs.has_key('a461'): kwargs['a461'] = ''
        if not kwargs.has_key('a462'): kwargs['a462'] = ''
        if not kwargs.has_key('a512'): kwargs['a512'] = ''
        if not kwargs.has_key('a514'): kwargs['a514'] = ''
        if not kwargs.has_key('a931'): kwargs['a931'] = ''
        if not kwargs.has_key('a932'): kwargs['a932'] = ''
        if not kwargs.has_key('a941'): kwargs['a941'] = ''
        if not kwargs.has_key('a942'): kwargs['a942'] = ''
        if not kwargs.has_key('a943'): kwargs['a943'] = ''
        if not kwargs.has_key('a1014'): kwargs['a1014'] = ''
        if not kwargs.has_key('a1015'): kwargs['a1015'] = ''
        if not kwargs.has_key('a1018'): kwargs['a1018'] = ''
        if not kwargs.has_key('a1019'): kwargs['a1019'] = ''
        if not kwargs.has_key('b111'): kwargs['b111'] = ''
        if not kwargs.has_key('b112'): kwargs['b112'] = ''
        if not kwargs.has_key('b212'): kwargs['b212'] = ''
        if not kwargs.has_key('b222'): kwargs['b222'] = ''
        if not kwargs.has_key('b241'): kwargs['b241'] = ''
        if not kwargs.has_key('b251'): kwargs['b251'] = ''
        if not kwargs.has_key('b261'): kwargs['b261'] = ''
        if not kwargs.has_key('b311'): kwargs['b311'] = ''
        if not kwargs.has_key('b314'): kwargs['b314'] = ''
        if not kwargs.has_key('b315'): kwargs['b315'] = ''
        if not kwargs.has_key('b316'): kwargs['b316'] = ''
        if not kwargs.has_key('b412'): kwargs['b412'] = ''
        if not kwargs.has_key('c121'): kwargs['c121'] = ''
        if not kwargs.has_key('c131'): kwargs['c131'] = ''
        if not kwargs.has_key('c132'): kwargs['c132'] = ''
        if not kwargs.has_key('c133'): kwargs['c133'] = ''

        #check if the user didn't already answer
        if self.check_if_answered(REQUEST):
            return REQUEST.RESPONSE.redirect(self.absolute_url())

        #check template deadline
        if not self.check_template_deadline():
            return REQUEST.RESPONSE.redirect(self.absolute_url())

        for key, value in kwargs.items():
            if not (key.endswith('P') or key.endswith('S') or key.endswith('T') or key.endswith('C')):
                if value:
                    continue
                self.setSessionErrors(['Please answer all fields.'])
                return REQUEST.RESPONSE.redirect(self.absolute_url())

        REQUEST.SESSION.clear()
        addNySurveyAnswer(self, REQUEST=REQUEST, **kwargs)

    #view answers and statistics for this survey template
    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_statistics')
    manage_statistics = PageTemplateFile('zpt/manage_template_statistics_html', globals())

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_statistics_inf')
    manage_statistics_inf = PageTemplateFile('zpt/manage_template_statistics_inf_html', globals())

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_statistics_counted')
    manage_statistics_counted = PageTemplateFile('zpt/manage_template_statistics_counted_html', globals())

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_statistics_counted_inf')
    manage_statistics_counted_inf = PageTemplateFile('zpt/manage_template_statistics_counted_inf_html', globals())

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_statistics_colored')
    manage_statistics_colored = PageTemplateFile('zpt/manage_template_statistics_colored_html', globals())

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'manage_answers')
    manage_answers = PageTemplateFile('zpt/manage_answers_html', globals())

    def __init__(self, id='', title='', date=''):
        self.id = id
        self.title = title
        self.date = date

    #api
    def get_template_object(self):
        return self

    def get_template_path(self, p=0):
        return self.absolute_url(p)

    def get_template_answers(self):
        return self.objectValues(METATYPE_NYSURVEY_ANSWER)

    def get_country_class(self, aw='N'):
        if aw == 'Ma':
            return 'major'
        if aw == 'Mi':
            return 'minor'
        if aw == 'Me':
            return 'medium'
        return 'none'

    def count_answers(self):
        return len(self.get_template_answers())

    def check_if_answered(self, REQUEST=None):
        """
        Checks if the current user allready answered this template.
        """

        user = REQUEST.AUTHENTICATED_USER.getUserName()
        if user == 'Anonymous User': return None # don't check for anonymous
        return user in [answer.user for answer in self.get_template_answers()]

    def check_template_deadline(self):
        """
        True if deadline not reached.
        """
        today = self.utGetTodayDate()
        return today.lessThanEqualTo(self.utConvertStringToDateTimeObj(self.date))

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'get_statistics')
    def get_statistics(self):
        """ """
        answer_count = self.count_answers()
        res = {}
        for answer in self.get_template_answers():
            for answer_attr in answer.get_attrs():
                if getattr(answer, answer_attr, '') == 'N':
                    if not res.has_key(answer_attr + '_N'):
                        res[answer_attr + '_N'] = []
                    res[answer_attr + '_N'].append(answer)
                if getattr(answer, answer_attr, '') == 'Mi':
                    if not res.has_key(answer_attr + '_Mi'):
                        res[answer_attr + '_Mi'] = []
                    res[answer_attr + '_Mi'].append(answer)
                if getattr(answer, answer_attr, '') == 'Me':
                    if not res.has_key(answer_attr + '_Me'):
                        res[answer_attr + '_Me'] = []
                    res[answer_attr + '_Me'].append(answer)
                if getattr(answer, answer_attr, '') == 'Ma':
                    if not res.has_key(answer_attr + '_Ma'):
                        res[answer_attr + '_Ma'] = []
                    res[answer_attr + '_Ma'].append(answer)

        ret = {}
        for key, value in res.items():
            z_key = key.split('_')[0]
            if not ret.has_key(z_key):
                ret[z_key] = {'N': 0, 'Mi': 0, 'Me': 0, 'Ma': 0}
            if key.endswith('N'):
                ret[z_key]['N'] = (len(value)*100)/answer_count
            if key.endswith('Mi'):
                ret[z_key]['Mi'] = (len(value)*100)/answer_count
            if key.endswith('Me'):
                ret[z_key]['Me'] = (len(value)*100)/answer_count
            if key.endswith('Ma'):
                ret[z_key]['Ma'] = (len(value)*100)/answer_count
        return ret

    def count_attr_value(self, attr, value, suffixes=('P', 'S', 'T')):
        answers = self.get_template_answers()
        count = 0
        if isinstance(suffixes, str):
            suffixes = (suffixes,)
        for answer in answers:
            for suffix in suffixes:
                if getattr(answer, attr + suffix, '') == value:
                    count += 1
        return count

    def percent_attr_value(self, attr, value):
        count = self.count_attr_value(attr, value)
        return count * 100.0 / (self.count_answers() * 3)

    security.declareProtected(PERMISSION_NYSURVEY_ADMINISTRATE, 'get_statistics_counted')
    def get_statistics_counted(self):
        """ """
        res = {}
        for answer in self.get_template_answers():
            for answer_attr in answer.get_attrs():
                if getattr(answer, answer_attr, '') == 'N':
                    if not res.has_key(answer_attr + '_N'):
                        res[answer_attr + '_N'] = []
                    res[answer_attr + '_N'].append(answer)
                if getattr(answer, answer_attr, '') == 'Mi':
                    if not res.has_key(answer_attr + '_Mi'):
                        res[answer_attr + '_Mi'] = []
                    res[answer_attr + '_Mi'].append(answer)
                if getattr(answer, answer_attr, '') == 'Me':
                    if not res.has_key(answer_attr + '_Me'):
                        res[answer_attr + '_Me'] = []
                    res[answer_attr + '_Me'].append(answer)
                if getattr(answer, answer_attr, '') == 'Ma':
                    if not res.has_key(answer_attr + '_Ma'):
                        res[answer_attr + '_Ma'] = []
                    res[answer_attr + '_Ma'].append(answer)

        ret = {}
        for key, value in res.items():
            z_key = key.split('_')[0]
            if not ret.has_key(z_key):
                ret[z_key] = {'N': 0, 'Mi': 0, 'Me': 0, 'Ma': 0}
            if key.endswith('N'):
                ret[z_key]['N'] = len(value)
            if key.endswith('Mi'):
                ret[z_key]['Mi'] = len(value)
            if key.endswith('Me'):
                ret[z_key]['Me'] = len(value)
            if key.endswith('Ma'):
                ret[z_key]['Ma'] = len(value)
        return ret

    def get_template_date(self):
        """Returns the maximum date of the template"""
        return self.date

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, date='', REQUEST=None):
        """Modify template properties"""
        if date: self.date = date
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/template_manage_edit', globals())

InitializeClass(NySurveyTemplate)
