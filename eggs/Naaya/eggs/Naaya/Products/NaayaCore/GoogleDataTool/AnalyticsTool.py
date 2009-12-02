import cgi
import gdata.auth
import gdata.analytics.service
import locale
import time
import datetime

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS, MESSAGE_SAVEDCHANGES
from Products.NaayaCore.managers.utils import utils

SCOPE = 'https://www.google.com/analytics/feeds/'
SOURCE = 'naaya-statistics-v1'
INTERVALS = [
                {'period': 30, 'value': 'Last month'},
                {'period': 90, 'value': 'Last 3 months'},
                {'period': 180, 'value': 'Last 6 months'},
                {'period': 356, 'value': 'Last year'}
            ]

#@todo: ask alex morega about this
locale.setlocale(locale.LC_ALL, "")

def manage_addAnalyticsTool(self, REQUEST=None):
    """ """
    ob = AnalyticsTool(ID_ANALYTICSTOOL, TITLE_ANALYTICSTOOL)
    self._setObject(ID_ANALYTICSTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class AnalyticsTool(SimpleItem, utils):
    """ """

    meta_type = METATYPE_ANALYTICSTOOL
    icon = 'misc_/NaayaCore/AnalyticsTool.gif'

    manage_options = (
        {'label': 'Accounts', 'action': 'admin_account'},
        ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.ga_service = gdata.analytics.service.AccountsService(source=SOURCE)
        self.gd_service = gdata.analytics.service.AnalyticsDataService(source=SOURCE)
        self.account = None
        self.date_interval = 30
        self.start_date = ''

    #administration
    def index_html(self, REQUEST):
        """ redirect to admin_account """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_account')

    _admin_account_zpt = NaayaPageTemplateFile('zpt/account', globals(), 'site_admin_account')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_stats')
    admin_stats = NaayaPageTemplateFile('zpt/stats', globals(), 'site_admin_stats')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_account')
    def admin_account(self, REQUEST):
        """ Administration page for Google accounts """
        authorization = self.checkAuthorization()
        if authorization:
            #display accounts
            if REQUEST.has_key('save'):
                account = REQUEST.get('account', '')
                date_interval = REQUEST.get('date_interval', '')
                start_date = REQUEST.get('start_date', '')
                if account:
                    self.account = account
                if start_date:
                    self.start_date = start_date
                    self.date_interval = 0
                else:
                    self.date_interval = int(date_interval)
                    self.start_date = ''
                if self.account or self.start_date or self.date_interval:
                    self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            elif REQUEST.has_key('revoke'):
                self.delAuthToken()
                REQUEST.set('auth_url', self.generateAuthUrl(self.REQUEST.URL))
                return self._admin_account_zpt(REQUEST)
            REQUEST.set('accounts', self.getAccounts())
        else:
            #get authorization
            if REQUEST.has_key('token') and not REQUEST.has_key('revoke'):
                self.getAuthToken(uri='%s?%s' % (self.REQUEST.URL, self.REQUEST.QUERY_STRING))
                REQUEST.set('accounts', self.getAccounts()) #display accounts
            else:
                REQUEST.set('auth_url', self.generateAuthUrl(self.REQUEST.URL))
        return self._admin_account_zpt(REQUEST)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'generateAuthUrl')
    def generateAuthUrl(self, uri):
        """ generate authentication URL """
        return gdata.auth.GenerateAuthSubUrl(uri, SCOPE, secure=False, session=True)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getAuthToken')
    def getAuthToken(self, uri):
        """ extract and store authentication token """
        token = gdata.auth.extract_auth_sub_token_from_url(uri)
        self.ga_service.UpgradeToSessionToken(token)
        self.gd_service.token_store.add_token(token)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'delAuthToken')
    def delAuthToken(self):
        """ revoke authentication token """
        self.ga_service.RevokeAuthSubToken()
        self.gd_service.RevokeAuthSubToken()
        self.account = None

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getAccounts')
    def getAccounts(self):
        """ get accounts list """
        res = []
        try:
            account = self.ga_service.GetAccountList()
        except gdata.service.RequestError:
            return None
        if account.entry:
            for entry in account.entry:
                res.append((entry.tableId[0].text, entry.title.text))
            return res

    def getVisitsGraph(self):
        """ Get the visitors graph """
        sd, ed = self.get_date_interval()
        try:
            data = self.gd_service.GetData(
                        ids=self.account, 
                        start_date=sd.strftime('%Y-%m-%d'), 
                        end_date=ed.strftime('%Y-%m-%d'),
                        dimensions='ga:date', 
                        metrics='ga:visits',
                        sort='ga:date')
        except gdata.service.RequestError:
            return None
        valid = False
        if data.entry:
            maximum = 0
            res = []
            for stats in data.entry:
                visit_value = int(stats.visits.value)
                if visit_value > maximum:
                    maximum = visit_value
                if visit_value and not valid:
                    valid = True    #check for 0 values
                res.append(stats.visits.value)
            if valid:
                #chart values, y-axis maxi value, y-axis intermediate values, x-axis labels
                return ','.join(res), maximum*1.1, '||%s|%s|%s|%s|' % (maximum/3, maximum/2, 2*maximum/3, maximum), '|%s|%s|' % (sd.strftime('%d %b'), ed.strftime('%d %b'))

    def getSiteSummary(self):
        """ Get esential date about site usage """
        sd, ed = self.get_date_interval()
        try:
            data = self.gd_service.GetData(
                        ids=self.account, 
                        start_date=sd.strftime('%Y-%m-%d'), 
                        end_date=ed.strftime('%Y-%m-%d'),
                        metrics='ga:visits,ga:visitors,ga:pageviews,ga:timeOnSite')
        except gdata.service.RequestError:
            return None
        if data.entry:
            res = {}
            #take the first entry
            stats = data.entry[0]
            res['visits'] = locale.format('%d', float(stats.visits.value), True)
            res['visitors'] = locale.format('%d', float(stats.visitors.value), True)
            res['pageviews'] = locale.format('%d', float(stats.pageviews.value), True)
            res['timeOnSite'] = humanize_time(float(stats.timeOnSite.value)/float(stats.visits.value))
            return res

    def getSiteUsage(self):
        """ Get the site usage """
        sd, ed = self.get_date_interval()
        try:
            data = self.gd_service.GetData(
                        ids=self.account, 
                        start_date=sd.strftime('%Y-%m-%d'), 
                        end_date=ed.strftime('%Y-%m-%d'),
                        metrics='ga:visits,ga:bounces,ga:pageviews,ga:timeOnSite,ga:newVisits,ga:entrances')
        except gdata.service.RequestError:
            return None
        if data.entry:
            res = {}
            #take the first entry
            stats = data.entry[0]
            res['visits'] = locale.format('%d', float(stats.visits.value), True)
            bounce_rate = float(stats.bounces.value)/float(stats.entrances.value)*100
            res['bounces'] = '%.2f%%' % bounce_rate
            pages_visit = float(stats.pageviews.value)/float(stats.visits.value)
            res['pages_visit'] = '%.2f' % pages_visit
            res['pageviews'] = locale.format('%d', float(stats.pageviews.value), True)
            res['timeOnSite'] = humanize_time(float(stats.timeOnSite.value)/float(stats.visits.value))
            newVisits = float(stats.newVisits.value)/float(stats.visits.value)*100
            res['newVisits'] = '%.2f%%' % newVisits
            return res

    def getTopPages(self):
        """ Get the top pages """
        sd, ed = self.get_date_interval()
        try:
            data = self.gd_service.GetData(
                        ids=self.account, 
                        start_date=sd.strftime('%Y-%m-%d'), 
                        end_date=ed.strftime('%Y-%m-%d'),
                        dimensions='ga:pagePath', 
                        metrics='ga:pageviews',
                        sort='-ga:pageviews', 
                        max_results='10')
        except gdata.service.RequestError:
            return None

        website_uri = ''
        if data.extension_elements:
            for elem in data.extension_elements:
                if elem.tag == 'dataSource':
                    for child in elem.children:
                        if child.tag == 'tableName':
                            website_uri = 'http://%s' % child.text
                            break
        if data.entry:
            res = []
            for stats in data.entry:
                dic = {}
                dic['pagePath'] = stats.pagePath.value
                dic['pageviews'] = locale.format('%d', float(stats.pageviews.value), True)
                res.append(dic)
            return res, website_uri

    def getTopReferers(self):
        """ Get the top referers """
        sd, ed = self.get_date_interval()
        try:
            data = self.gd_service.GetData(
                        ids=self.account, 
                        start_date=sd.strftime('%Y-%m-%d'), 
                        end_date=ed.strftime('%Y-%m-%d'),
                        dimensions='ga:source', 
                        metrics='ga:visits',
                        filters='ga:medium==referral',
                        sort='-ga:visits', 
                        max_results='10')
        except gdata.service.RequestError:
            return None
        if data.entry:
            res = []
            for stats in data.entry:
                dic = {}
                dic['source'] = stats.source.value
                dic['visits'] = locale.format('%d', float(stats.visits.value), True)
                res.append(dic)
            return res

    def getTopSearches(self):
        """ Get the top searches """
        sd, ed = self.get_date_interval()
        try:
            data = self.gd_service.GetData(
                        ids=self.account, 
                        start_date=sd.strftime('%Y-%m-%d'), 
                        end_date=ed.strftime('%Y-%m-%d'),
                        dimensions='ga:keyword', 
                        metrics='ga:visits',
                        filters='ga:keyword!=(not set)',
                        sort='-ga:visits', 
                        max_results='10')
        except gdata.service.RequestError:
            return None
        if data.entry:
            res = []
            for stats in data.entry:
                dic = {}
                dic['keyword'] = stats.keyword.value
                dic['visits'] = locale.format('%d', float(stats.visits.value), True)
                res.append(dic)
            return res

    def checkAuthorization(self):
        """ check authorization """
        try:
            return self.gd_service.AuthSubTokenInfo()
        except:
            return None

    def get_date_interval(self):
        """ """
        end_date = datetime.datetime.today()
        if self.start_date:
            sd = time.strptime(self.start_date,'%d/%m/%Y')
            start_date = datetime.datetime(*sd[0:6])
        else:
            start_date = end_date - datetime.timedelta(days=self.date_interval)
        return start_date, end_date

    def get_intervals(self):
        """ """
        return INTERVALS

InitializeClass(AnalyticsTool)


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)