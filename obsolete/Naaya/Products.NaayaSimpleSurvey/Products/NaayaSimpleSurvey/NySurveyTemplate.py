#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from AccessControl.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from .constants import *
from .NySurveyAnswer import manage_addNySurveyAnswer_html, addNySurveyAnswer, answer_add_html

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

        if not 'a113' in kwargs: kwargs['a113'] = ''
        if not 'a114' in kwargs: kwargs['a114'] = ''
        if not 'a115' in kwargs: kwargs['a115'] = ''
        if not 'a123' in kwargs: kwargs['a123'] = ''
        if not 'a131' in kwargs: kwargs['a131'] = ''
        if not 'a211' in kwargs: kwargs['a211'] = ''
        if not 'a212' in kwargs: kwargs['a212'] = ''
        if not 'a213' in kwargs: kwargs['a213'] = ''
        if not 'a214' in kwargs: kwargs['a214'] = ''
        if not 'a217' in kwargs: kwargs['a217'] = ''
        if not 'a218' in kwargs: kwargs['a218'] = ''
        if not 'a219' in kwargs: kwargs['a219'] = ''
        if not 'a221' in kwargs: kwargs['a221'] = ''
        if not 'a222' in kwargs: kwargs['a222'] = ''
        if not 'a231' in kwargs: kwargs['a231'] = ''
        if not 'a241' in kwargs: kwargs['a241'] = ''
        if not 'a242' in kwargs: kwargs['a242'] = ''
        if not 'a243' in kwargs: kwargs['a243'] = ''
        if not 'a244' in kwargs: kwargs['a244'] = ''
        if not 'a251' in kwargs: kwargs['a251'] = ''
        if not 'a252' in kwargs: kwargs['a252'] = ''
        if not 'a311' in kwargs: kwargs['a311'] = ''
        if not 'a312' in kwargs: kwargs['a312'] = ''
        if not 'a314' in kwargs: kwargs['a314'] = ''
        if not 'a315' in kwargs: kwargs['a315'] = ''
        if not 'a321' in kwargs: kwargs['a321'] = ''
        if not 'a322' in kwargs: kwargs['a322'] = ''
        if not 'a323' in kwargs: kwargs['a323'] = ''
        if not 'a324' in kwargs: kwargs['a324'] = ''
        if not 'a352' in kwargs: kwargs['a352'] = ''
        if not 'a411' in kwargs: kwargs['a411'] = ''
        if not 'a414' in kwargs: kwargs['a414'] = ''
        if not 'a412' in kwargs: kwargs['a412'] = ''
        if not 'a431' in kwargs: kwargs['a431'] = ''
        if not 'a461' in kwargs: kwargs['a461'] = ''
        if not 'a462' in kwargs: kwargs['a462'] = ''
        if not 'a512' in kwargs: kwargs['a512'] = ''
        if not 'a514' in kwargs: kwargs['a514'] = ''
        if not 'a931' in kwargs: kwargs['a931'] = ''
        if not 'a932' in kwargs: kwargs['a932'] = ''
        if not 'a941' in kwargs: kwargs['a941'] = ''
        if not 'a942' in kwargs: kwargs['a942'] = ''
        if not 'a943' in kwargs: kwargs['a943'] = ''
        if not 'a1014' in kwargs: kwargs['a1014'] = ''
        if not 'a1015' in kwargs: kwargs['a1015'] = ''
        if not 'a1018' in kwargs: kwargs['a1018'] = ''
        if not 'a1019' in kwargs: kwargs['a1019'] = ''
        if not 'b111' in kwargs: kwargs['b111'] = ''
        if not 'b112' in kwargs: kwargs['b112'] = ''
        if not 'b212' in kwargs: kwargs['b212'] = ''
        if not 'b222' in kwargs: kwargs['b222'] = ''
        if not 'b241' in kwargs: kwargs['b241'] = ''
        if not 'b251' in kwargs: kwargs['b251'] = ''
        if not 'b261' in kwargs: kwargs['b261'] = ''
        if not 'b311' in kwargs: kwargs['b311'] = ''
        if not 'b314' in kwargs: kwargs['b314'] = ''
        if not 'b315' in kwargs: kwargs['b315'] = ''
        if not 'b316' in kwargs: kwargs['b316'] = ''
        if not 'b412' in kwargs: kwargs['b412'] = ''
        if not 'c121' in kwargs: kwargs['c121'] = ''
        if not 'c131' in kwargs: kwargs['c131'] = ''
        if not 'c132' in kwargs: kwargs['c132'] = ''
        if not 'c133' in kwargs: kwargs['c133'] = ''

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
                    if not answer_attr + '_N' in res:
                        res[answer_attr + '_N'] = []
                    res[answer_attr + '_N'].append(answer)
                if getattr(answer, answer_attr, '') == 'Mi':
                    if not answer_attr + '_Mi' in res:
                        res[answer_attr + '_Mi'] = []
                    res[answer_attr + '_Mi'].append(answer)
                if getattr(answer, answer_attr, '') == 'Me':
                    if not answer_attr + '_Me' in res:
                        res[answer_attr + '_Me'] = []
                    res[answer_attr + '_Me'].append(answer)
                if getattr(answer, answer_attr, '') == 'Ma':
                    if not answer_attr + '_Ma' in res:
                        res[answer_attr + '_Ma'] = []
                    res[answer_attr + '_Ma'].append(answer)

        ret = {}
        for key, value in res.items():
            z_key = key.split('_')[0]
            if not z_key in ret:
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
                    if not answer_attr + '_N' in res:
                        res[answer_attr + '_N'] = []
                    res[answer_attr + '_N'].append(answer)
                if getattr(answer, answer_attr, '') == 'Mi':
                    if not answer_attr + '_Mi' in res:
                        res[answer_attr + '_Mi'] = []
                    res[answer_attr + '_Mi'].append(answer)
                if getattr(answer, answer_attr, '') == 'Me':
                    if not answer_attr + '_Me' in res:
                        res[answer_attr + '_Me'] = []
                    res[answer_attr + '_Me'].append(answer)
                if getattr(answer, answer_attr, '') == 'Ma':
                    if not answer_attr + '_Ma' in res:
                        res[answer_attr + '_Ma'] = []
                    res[answer_attr + '_Ma'].append(answer)

        ret = {}
        for key, value in res.items():
            z_key = key.split('_')[0]
            if not z_key in ret:
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
