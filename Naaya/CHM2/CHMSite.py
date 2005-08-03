# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from urlparse import urlparse

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker

manage_addCHMSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addCHMSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, CHMSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class CHMSite(NySite):
    """ """

    meta_type = METATYPE_CHMSITE
    icon = 'misc_/CHM2/Site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        NySite.__dict__['loadDefaultData'](self)
        manage_addLinkChecker(self, ID_LINKCHECKER, TITLE_LINKCHECKER)
        self.loadSkeleton(join(CHM2_PRODUCT_PATH, 'skel'))

    #objects getters
    def getLinkChecker(self): return self._getOb(ID_LINKCHECKER, None)
    def getLinkCheckerLastLog(self):
        try:
            entries = self.utSortObjsListByAttr(self._getOb(ID_LINKCHECKER).objectValues('LogEntry'), 'date_create', p_desc=1)
            if len(entries) > 0: return entries[0]
            else: return None
        except:
            return None
    #api
    def getOnFrontNews(self):
        #returns a list with the news marked as on front
        #this requires NyNews pluggable content type to be present
        news_ob = self._getOb('news', None)
        if news_ob is not None:
            return [x for x in news_ob.objectValues(METATYPE_NYNEWS) if x.approved==1 and x.topitem==1]
        else:
            return []

    def getUrlMap(self, sort='title'):
        #process and returns a map with all approved urls in the portal by domain
        #this requires NyURL pluggable content type to be present
        urls = self.query_objects_ex(meta_type=METATYPE_NYURL, approved=1)
        if sort=='title' or sort=='locator':
            return self.utSortObjsListByAttr(urls, sort, 0)
        elif sort=='server':
            domains = {}
            for url in urls:
                domain = urlparse(url.locator)[1]
                domain = domain.replace('www.', '')
                domain_key = domain.split('.')
                domain_key = domain_key[:-1]
                domain_key.reverse()
                domain_key = '.'.join(domain_key)
                if not domains.has_key(domain_key):
                    domains[domain_key] = [domain, []]
                domains[domain_key][1].append(url)
            domains_keys = domains.keys()
            domains_keys.sort()
            return domains_keys, domains
        else:
            return urls

    def getURLProperties(self):
        #process the list of all approved items which have URL properties, by location
        url_struct = {}
        print self.query_objects_ex(meta_type=[METATYPE_NYURL, METATYPE_NYEVENT, METATYPE_NYNEWS])
        for url in self.query_objects_ex(meta_type=[METATYPE_NYURL, METATYPE_NYEVENT, METATYPE_NYNEWS]):
            if url.meta_type == METATYPE_NYURL:
                url_prop = ['locator']
            elif url.meta_type == METATYPE_NYNEWS:
                url_prop = ['resourceurl']
            elif url.meta_type == METATYPE_NYEVENT:
                url_prop = ['location_url', 'agenda_url', 'event_url']
            for p in url_prop:
                p_value = getattr(url, p)
                if url_struct.has_key(p_value):
                    url_struct[p_value][1].append(url.getParentNode())
                else:
                    url_struct[p_value] = [url, [url.getParentNode()]]
        return url_struct

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_urls_html')
    def admin_urls_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_urls')

    security.declareProtected(PERMISSION_ADMINISTRATE, 'admin_submissions_html')
    def admin_submissions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_submissions')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'admin_deletions_html')
    def admin_deletions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_deletions')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_urls_html')
    def admin_urls_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_urls')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkchecker_html')
    def admin_linkchecker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkchecker')

    #site pages
    security.declareProtected(view, 'urlmap_html')
    def urlmap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_urlmap')

InitializeClass(CHMSite)
