from DateTime import DateTime
from Acquisition import Implicit
from naaya.i18n.LocalPropertyManager import LocalProperty

from Products.NaayaBase.NyProperties import NyProperties

class questionnaire_item(Implicit, NyProperties):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def __init__(self, title, description, coverage, keywords,
                 sortorder, releasedate, expirationdate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords,
            sortorder, releasedate, expirationdate, lang)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title='', description='', coverage='',
                        keywords='', sortorder=100,
                        releasedate=DateTime(), expirationdate=DateTime(),
                        notify_owner=True,
                        notify_respondents='LET_THEM_CHOOSE_YES',
                        lang=None, **kwargs):
        """
        Save item properties.
        """
        assert(notify_respondents in ('ALWAYS', 'NEVER', 'LET_THEM_CHOOSE_YES',
                                      'LET_THEM_CHOOSE_NO'))
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.releasedate = releasedate
        self.expirationdate = expirationdate
        self.notify_owner = notify_owner
        self.notify_respondents = notify_respondents
        self.allow_overtime = int(kwargs.get('allow_overtime', '0'))
        self.allow_multiple_answers = int(kwargs.get('allow_multiple_answers',
                                                     '0'))
        self.allow_drafts = int(kwargs.get('allow_drafts', '0'))
        self.contributor = kwargs.get('contributor')
