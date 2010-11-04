our_acronyms = [s.encode('utf-8') for s in (
    u'Assessment',
    u'Environmental Impact Assessment (EIA)',
    u'Strategic Impact Assessment (SIA)',
    u'Impact assessment',
    u'Impact Assessment',
    u'Impact assessments',
    u'Environmental Impact Assessment',
    u'Strategic Impact Assessment',
    u'Integrated assessment',
    u'Integrated assessments',
    u'Sectoral assessment',
    u'Sectoral assessments',
    u'Status and trend (or process) assessment',
    u'Thematic assessment',
    u'Thematic assessments',
    u'Ecosystem',
    u'Ecosystems',
    u'Response assessment',
    u'Response assessments',
    u'INSPIRE',
    u'GMES',
    u'Reportnet',
    u'Metadata',
    u'DPSIR',
    u'\u041e\u0446\u0435\u043d\u043a\u0438',
    u'\u041e\u0446\u0435\u043d\u043a\u0430',
    u'\u0414\u043e\u0441\u0442\u043e\u0432\u0435\u0440\u043d\u043e\u0441\u0442\u044c',
    u'\u042d\u043a\u043e\u0441\u0438\u0441\u0442\u0435\u043c\u0430',
    u'\u0414\u0421-\u0414-\u0421-\u0412-\u0420',
    u'\u041e\u0446\u0435\u043d\u043a\u0430 \u0432\u043e\u0437\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
    u'\u041e\u0446\u0435\u043d\u043a\u0438 \u0432\u043e\u0437\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
    u'\u0418\u043d\u0442\u0435\u0433\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u043e\u0446\u0435\u043d\u043a\u0430',
    u'\u0418\u043d\u0442\u0435\u0433\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u043e\u0446\u0435\u043d\u043a\u0438',
    u'\u041b\u0435\u0433\u0438\u0442\u0438\u043c\u043d\u043e\u0441\u0442\u044c',
    u'\u041c\u0435\u0442\u0430\u0434\u0430\u043d\u043d\u044b\u0435',
    u'\u0410\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c',
    u'\u041e\u0446\u0435\u043d\u043a\u0430 \u0440\u0435\u0430\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
    u'\u041e\u0446\u0435\u043d\u043a\u0438 \u0440\u0435\u0430\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
    u'\u0421\u0435\u043a\u0442\u043e\u0440\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430',
    u'\u0421\u0435\u043a\u0442\u043e\u0440\u0430\u043b\u044c\u043d\u044b\u0435 \u043e\u0446\u0435\u043d\u043a\u0438',
    u'\u041e\u0446\u0435\u043d\u043a\u0430 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f \u0438 \u0442\u0435\u043d\u0434\u0435\u043d\u0446\u0438\u0439 (\u0438\u043b\u0438 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0432)',
    u'\u0422\u0435\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430',
    u'\u0422\u0435\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u043e\u0446\u0435\u043d\u043a\u0438',
)]

site = container.getSite()
try:
    acronyms = site.database.acronyms.sql_methods.select_acronyms()
except:
    container.getSite().log_current_error()
    acronyms = []

gettext = site.getPortalTranslations()
acronym_map = [( gettext(a.acronym), gettext(a.name) )
               for a in acronyms if a.acronym in our_acronyms]
return acronym_map
