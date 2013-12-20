"""Fetch data from Google Analytics.

Requires the configuration of two environment variables:
`GOOGLE_AUTH_CLIENT_ID` and `GOOGLE_AUTH_CLIENT_SECRET`. Get them from the
Google `API Console`_.

.. _API Console: https://code.google.com/apis/console/

To generate a new set of keys, from the API console, click on "Create client
ID" and choose "installed application". Avoid committing the secret key to any
code repository.
"""

import os
import time
import datetime
import urllib

from zope.i18n.locales import locales
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS, MESSAGE_SAVEDCHANGES
from Products.NaayaCore.managers.utils import utils
from naaya.core.zope2util import json_response
from naaya.core.backport import requests

GOOGLE_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_ANALYTICS_API = 'https://www.googleapis.com/analytics/v3/'
INTERVALS = [
                {'period': 30, 'value': 'Last month'},
                {'period': 90, 'value': 'Last 3 months'},
                {'period': 180, 'value': 'Last 6 months'},
                {'period': 356, 'value': 'Last year'}
            ]

en = locales.getLocale('en')
formatter = en.numbers.getFormatter('decimal')
formatter.setPattern('#,##0;-#,##0')

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

    security = ClassSecurityInfo()

    _google_access_token = None
    _google_refresh_token = None
    profile_code = None
    profile = None

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self._reset()

    def _reset(self):
        self.account = None
        self.date_interval = 30
        self.start_date = ''
        self.ga_id = '' # Google Analytics web property ID (UA-number)
        self.gw_verify = '' # Google Webmaster verification meta tag
        self._google_access_token = None
        self._google_refresh_token = None
        self.profile_code = None
        self.profile = None
        self.clear_cache()

    #cache
    def _set_cache(self, data, view_name):
        self._cache[view_name] = data
        self._cache_timestamp = datetime.datetime.now()

    security.declarePrivate('get_cache')
    def get_cache(self, view_name):
        interval = datetime.datetime.now() - self._cache_timestamp
        if interval.days > 0:
            return None
        return self._cache.get(view_name, None)

    security.declarePrivate('get_cache')
    def clear_cache(self):
        self._cache = {}
        self._cache_timestamp = datetime.datetime.now()

    #administration
    def index_html(self, REQUEST):
        """ redirect to admin_account """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_account')

    _admin_account_zpt = NaayaPageTemplateFile('zpt/account', globals(), 'site_admin_account')
    _admin_verify = NaayaPageTemplateFile('zpt/verify', globals(), 'site_admin_verify')
    _stats_info = NaayaPageTemplateFile('zpt/stats_info', globals(), 'site_admin_stats_info')

    _admin_stats = NaayaPageTemplateFile('zpt/stats', globals(),
                                         'site_admin_stats')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_stats')
    def admin_stats(self, REQUEST):
        """ """
        if self._google_access_token is None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/authorize')
            return
        elif self.profile is None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_account')
            return
        return self._admin_stats()

    _authorize = NaayaPageTemplateFile('zpt/authorize', globals(),
                                       'site_admin_stats_authorize')
    def authorize(self):
        """ """
        is_configured = bool('GOOGLE_AUTH_CLIENT_ID' in os.environ and
                             'GOOGLE_AUTH_CLIENT_SECRET' in os.environ)
        return self._authorize(is_configured=is_configured)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'stats_info')
    def stats_info(self):
        """ """
        view_name = 'stats'
        cached_data = self.get_cache(view_name=view_name)
        if cached_data is None:
            # no data in the cache, so cache it
            data_to_cache = self._stats_info(self.REQUEST)
            self._set_cache(data_to_cache, view_name=view_name)
            return data_to_cache
        # get cached data
        return cached_data

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_verify')
    def admin_verify(self, REQUEST):
        """ Administration page for Google verification codes """
        if REQUEST.has_key('save'):
            self.ga_id = REQUEST.get('ga_id', '')
            self.gw_verify = REQUEST.get('gw_verify', '')
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        return self._admin_verify(REQUEST)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_account')
    def admin_account(self, REQUEST):
        """ Administration page for Google accounts """
        if self._google_access_token is None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/authorize')
            return

        options = {}
        if self.profile is None:
            options.update(choose_profile=True, accounts=self.getAccounts())

        else:
            options.update(choose_profile=False, profile_name="")
            profile_info = self._get_profile_info(self.account,
                                                  self.profile_code)
            if profile_info is not None:
                options['profile_name'] = profile_info['name']

        return self._admin_account_zpt(REQUEST, **options)

    def _update_access_token(self):
        if self._google_access_token is None:
            raise RuntimeError("Google access token is not set.")
        access_token, expiry = self._google_access_token
        if time.time() > expiry:
            code = self._google_refresh_token
            data = {
                'grant_type': 'refresh_token',
                'client_id': os.environ['GOOGLE_AUTH_CLIENT_ID'],
                'client_secret': os.environ['GOOGLE_AUTH_CLIENT_SECRET'],
                'refresh_token': code,
            }
            resp = requests.post(GOOGLE_TOKEN_URI, data)
            self._save_access_token(resp)
            access_token, expiry = self._google_access_token

        return access_token

    def _api_get(self, path, params={}):
        access_token = self._update_access_token()
        url = GOOGLE_ANALYTICS_API + path
        headers = {'Authorization': 'Bearer ' + access_token}
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError("API call error: %r (%r)" % (resp, resp.json))
        return resp.json

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getAccounts')
    def getAccounts(self):
        """ get accounts list """
        resp_json = self._api_get('management/accounts')
        return [(i['id'], i['name']) for i in resp_json['items']]

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getProfiles')
    def getProfiles(self, account, REQUEST=None):
        """ """
        resp_json = self._api_get('management/accounts/%s/webproperties'
                                  % account)
        data = {'profiles': [{'code': i['id'], 'name': i['name']}
                             for i in resp_json['items']]}

        if REQUEST is not None:
            return json_response(data, REQUEST.RESPONSE)
        else:
            return data

    def _get_profile_info(self, account, profile_code):
        resp_json = self._api_get('management/accounts/%s/'
                                  'webproperties/%s/profiles'
                                  % (account, profile_code))
        if 'items' not in resp_json:
            return None
        else:
            return resp_json['items'][0]

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_account_save')
    def admin_account_save(self, account=None, profile_code=None,
                           date_interval='30', start_date='', REQUEST=None):
        """ """
        if account:
            self.account = account

        if profile_code and self.profile is None:
            # We check `self.profile is None` in order to disallow changing
            # a profile. De-authorize the account first.
            profile_info = self._get_profile_info(self.account, profile_code)
            if profile_info is None:
                self.setSessionErrorsTrans(
                    "The site you selected is not available.")
            else:
                self.profile_code = profile_code
                self.profile = profile_info['id']

        if start_date:
            self.start_date = start_date
            self.date_interval = 0
        else:
            self.date_interval = int(date_interval or '30')
            self.start_date = ''
        if self.account or self.start_date or self.date_interval:
            self.clear_cache()  #clear cached data
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_account')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_account_revoke')
    def admin_account_revoke(self, REQUEST=None):
        """ """
        self._reset()
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_account')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'generateAuthUrl')
    def generateAuthUrl(self):
        """ generate authentication URL """
        query = {
            'response_type': 'code',
            'client_id': os.environ['GOOGLE_AUTH_CLIENT_ID'],
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'scope': GOOGLE_SCOPE,
            'access_type': 'offline',
        }
        return ('https://accounts.google.com/o/oauth2/auth?' +
                urllib.urlencode(query))

    def _save_access_token(self, resp):
        if 'error' in resp.json:
            raise RuntimeError("Error fetching new token: %r"
                               % resp.json['error'])
        assert resp.json['token_type'] == 'Bearer'
        expiry = time.time() + resp.json['expires_in']
        self._google_access_token = (resp.json['access_token'], expiry)
        if 'refresh_token' in resp.json:
            self._google_refresh_token = resp.json['refresh_token']

        import transaction
        transaction.get().note('(Saving new Google oauth2 token)')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveAuthorizationCode')
    def saveAuthorizationCode(self, code, REQUEST=None):
        """ """
        data = {
            'grant_type': 'authorization_code',
            'client_id': os.environ['GOOGLE_AUTH_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_AUTH_CLIENT_SECRET'],
            'code': code,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'scope': GOOGLE_SCOPE,
        }
        resp = requests.post(GOOGLE_TOKEN_URI, data)
        self._save_access_token(resp)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_account')

    def _api_get_ga_data(self, params):
        sd, ed = self.get_date_interval()
        params.setdefault('ids', 'ga:' + self.profile)
        params.setdefault('start-date', sd.strftime('%Y-%m-%d'))
        params.setdefault('end-date', ed.strftime('%Y-%m-%d'))
        return self._api_get('data/ga', params=params)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getVisitsGraph')
    def getVisitsGraph(self):
        """ Get the visitors graph """
        sd, ed = self.get_date_interval()
        data = self._api_get_ga_data({
            'dimensions': 'ga:date',
            'metrics': 'ga:visits',
            'sort': 'ga:date',
        })
        valid = False
        if 'rows' in data:
            maximum = 0
            res = []
            for row in data['rows']:
                visit_value = int(row[1])
                if visit_value > maximum:
                    maximum = visit_value
                if visit_value and not valid:
                    valid = True    #check for 0 values
                res.append(row[1])
            if valid:
                #chart values, y-axis maxi value, y-axis intermediate values, x-axis labels
                return ','.join(res), maximum*1.1, '||%s|%s|%s|%s|' % (maximum/3, maximum/2, 2*maximum/3, maximum), '|%s|%s|' % (sd.strftime('%d %b'), ed.strftime('%d %b'))

    security.declareProtected(view, 'getSiteSummary')
    def getSiteSummary(self):
        """ Get esential date about site usage """
        view_name = 'summary'
        if self.profile is None:
            return None

        cached_data = self.get_cache(view_name=view_name)
        if cached_data is not None:
            return cached_data

        data = self._api_get_ga_data({
            'metrics': 'ga:visits,ga:visitors,ga:pageviews,ga:timeOnSite',
        })
        if 'rows' in data:
            #take the first entry
            [stats] = self._data_rows(data)
            res = {
                'visits': formatter.format(float(stats['ga:visits'])),
                'visitors': formatter.format(float(stats['ga:visitors'])),
                'pageviews': formatter.format(float(stats['ga:pageviews'])),
                'timeOnSite': humanize_time(float(stats['ga:timeOnSite']) /
                                            float(stats['ga:visits'])),
            }
            # no data in the cache, so cache it
            self._set_cache(res, view_name=view_name)
            return res

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getSiteUsage')
    def getSiteUsage(self):
        """ Get the site usage """
        data = self._api_get_ga_data({
            'metrics': ('ga:visits,ga:bounces,ga:pageviews,'
                        'ga:timeOnSite,ga:newVisits,ga:entrances'),
        })
        if 'rows' in data:
            #take the first entry
            [stats] = self._data_rows(data)
            bounce_rate = (float(stats['ga:bounces']) /
                           float(stats['ga:entrances'])*100)
            pages_visit = (float(stats['ga:pageviews']) /
                           float(stats['ga:visits']))
            newVisits = (float(stats['ga:newVisits']) /
                         float(stats['ga:visits'])*100)
            return {
                'visits': formatter.format(float(stats['ga:visits'])),
                'bounces': '%.2f%%' % bounce_rate,
                'pages_visit': '%.2f' % pages_visit,
                'pageviews': formatter.format(float(stats['ga:pageviews'])),
                'timeOnSite': humanize_time(float(stats['ga:timeOnSite']) /
                                            float(stats['ga:visits'])),
                'newVisits': '%.2f%%' % newVisits,
            }

    def _data_rows(self, data):
        columns = [c['name'] for c in data['columnHeaders']]
        for row in data['rows']:
            yield dict(zip(columns, row))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getTopPages')
    def getTopPages(self):
        """ Get the top pages """
        data = self._api_get_ga_data({
            'dimensions': 'ga:pagePath',
            'metrics': 'ga:pageviews',
            'sort': 'ga:date',
            'sort': '-ga:pageviews',
            'max_results': '10',
        })
        if 'rows' in data:
            res = []
            for row in self._data_rows(data):
                res.append({
                    'pagePath': row['ga:pagePath'],
                    'pageviews': formatter.format(float(row['ga:pageviews']))
                })
            return res, ''

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getTopReferers')
    def getTopReferers(self):
        """ Get the top referers """
        data = self._api_get_ga_data({
            'dimensions': 'ga:source',
            'metrics': 'ga:visits',
            'filters': 'ga:medium==referral',
            'sort': '-ga:visits',
            'max_results': '10',
        })
        if 'rows' in data:
            res = []
            for row in self._data_rows(data):
                res.append({
                    'source': row['ga:source'],
                    'visits': formatter.format(float(row['ga:visits']))
                })
            return res

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getTopSearches')
    def getTopSearches(self):
        """ Get the top searches """
        data = self._api_get_ga_data({
            'dimensions': 'ga:keyword',
            'metrics': 'ga:visits',
            'filters': 'ga:keyword!=(not set)',
            'sort': '-ga:visits',
            'max_results': '10',
        })
        if 'rows' in data:
            res = []
            for row in self._data_rows(data):
                res.append({
                    'keyword': row['ga:keyword'],
                    'visits': formatter.format(float(row['ga:visits']))
                })
            return res

    security.declarePublic('get_date_interval')
    def get_date_interval(self):
        """ """
        end_date = datetime.datetime.today()
        if self.start_date:
            sd = time.strptime(self.start_date,'%d/%m/%Y')
            start_date = datetime.datetime(*sd[0:6])
        else:
            start_date = end_date - datetime.timedelta(days=self.date_interval)
        return start_date, end_date

    security.declarePublic('get_intervals')
    def get_intervals(self):
        """ """
        return INTERVALS

InitializeClass(AnalyticsTool)

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)
