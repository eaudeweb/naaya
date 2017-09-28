#Python imports
from sets import Set
import time
import urlparse
import urllib

#Zope imports
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass
from OFS.FindSupport import FindSupport
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zLOG import LOG, INFO, DEBUG

#Product's related imports
from Products.NaayaLinkChecker.Utils import *
from Products.NaayaLinkChecker.CheckerThread import CheckerThread
from Products.NaayaLinkChecker import LogEntry
from naaya.core.utils import force_to_unicode
from naaya.core.zope2util import folder_manage_main_plus

THREAD_COUNT = 4

manage_addLinkCheckerForm = PageTemplateFile('zpt/LinkCheckerForm', globals())
def manage_addLinkChecker(self, id, title, REQUEST=None):
    "Add a LinkChecker"
    ob = LinkChecker(id, title)
    self._setObject(id, ob)
    ob = self._getOb(id)
    if REQUEST:
        return self.manage_main(self,REQUEST)
    return ob.getId()

class LinkChecker(ObjectManager, SimpleItem, UtilsManager):
    """ Link checker is meant to check the links to remote websites """

    meta_type="Naaya LinkChecker"

    security = ClassSecurityInfo()

    manage_options = (ObjectManager.manage_options[0],) + \
          ({'label' : 'Properties', 'action' : 'manage_properties'},
          {'label' : 'Logs', 'action' : 'log_html'},) + SimpleItem.manage_options

    def __init__(self, id, title='',objectMetaType={}, proxy='', batch_size=10):
        "initialize a new instance of LinkChecker"
        self.id = id
        self.title = title
        self.objectMetaType = objectMetaType
        self.proxy = proxy
        self.batch_size = int(batch_size)
        self.use_catalog = 0
        self.catalog_name = ''
        self.ip_address = ''
        self.last_update = ''
        UtilsManager.__dict__['__init__'](self)

    def __setstate__(self,state):
        """ """
        if not hasattr(self, 'ip_address'):
            self.ip_address = ''
        LinkChecker.inheritedAttribute('__setstate__')(self, state)

    security.declareProtected(view_management_screens, 'manage_edit')
    def manage_edit(self, proxy, batch_size, title='', catalog_name='', ip_address='', REQUEST=None):
        """Edits the summary's characteristics"""
        self.title = title
        self.proxy = proxy
        self.batch_size = int(batch_size)
        self.ip_address = ip_address
        if REQUEST is not None:
            if REQUEST.has_key('use_catalog'):
                self.use_catalog = 1
                self.catalog_name = catalog_name
            else:
                self.use_catalog = 0
                self.catalog_name = ''
            REQUEST.RESPONSE.redirect('manage_properties')
        else:
            self.use_catalog = 1
            self.catalog_name = catalog_name

    security.declareProtected(view_management_screens, 'manage_addMetaType')
    def manage_addMetaType(self, MetaType=None, REQUEST=None):
        """Add a new meta type to list"""
        if MetaType is None:
            addmetatype = REQUEST.get('objectMetaType', '')
        else:
            addmetatype = MetaType
        if addmetatype != '':
            if addmetatype not in self.objectMetaType.keys():
                self.objectMetaType[addmetatype] = []
                self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens,'manage_delMetaType')
    def manage_delMetaType(self, REQUEST=None, **kwargs):
        """Delete meta types from list"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        delmetatype = kwargs.get('objectMetaType', [])
        for metatype in self.umConvertToList(delmetatype):
            try:
                del(self.objectMetaType[metatype])
            except:
                pass
        self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens, 'manage_addProperty')
    def manage_addProperty(self, MetaType=None, Property=None, multilingual=False, islink=False, REQUEST=None):
        """Add a new property for a meta type"""
        if MetaType is None:
            editmetatype = REQUEST.get('editmetatype', '')
            addobjectproperty = REQUEST.get('objectProperty', '')
        else:
            editmetatype = MetaType
            addobjectproperty = Property
        if self.hasMetaType(editmetatype):
            # valid meta type - add property
            listproperties = self.objectMetaType[editmetatype]
            if addobjectproperty != '':
                if addobjectproperty not in [p[0] for p in listproperties]:
                    listproperties.append((addobjectproperty, multilingual, islink))
                    self.objectMetaType[editmetatype] = listproperties
                    self._p_changed = 1
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('manage_properties?editmetatype=' + self.umURLEncode(editmetatype) + '#property')


    def getObjectMetaTypes(self):
        """Get all added meta types"""
        return self.objectMetaType.keys()

    security.declarePrivate('findObjects')
    def findObjects(self):
        """ find all the objects according with the LinkChecker criterias
        """
        mt = self.getObjectMetaTypes()
        if len(mt) == 0:
            return
        if self.use_catalog == 1:
            cat_obj = self.unrestrictedTraverse(self.catalog_name)
            objs = cat_obj({'meta_type':mt})
            for obj in objs:
                obj = cat_obj.getobject(obj.data_record_id_)
                if obj.absolute_url().find('Control_Panel') == -1:
                    yield obj
        else:
            objs = FindSupport().ZopeFind(self.umGetROOT(), obj_metatypes=mt, search_sub=1)
            for obj in objs:
                if obj[1].absolute_url().find('Control_Panel') == -1:
                    yield obj[1]

    security.declarePrivate('processObjects')
    def processObjects(self, limit=0):
        """Get a list of 'findObjects' results and for each result:
            - gets all specified properties
            - parse the content of each property and extract links
            - save results into a dictionary like {'obj_url':[list_of_links]}
        """
        results = {}
        all_urls = 0
        for obj in self.findObjects():
            if limit > 0:
                if len(results) >= limit:
                    break
            links = self.getLinksFromOb(obj)
            results[obj.absolute_url(1)] = links
            all_urls += len(links)
        return results, all_urls

    security.declarePrivate('processObject')
    def processObject(self, properties=[], context=''):
        """For the object obtained from context with unrestrictedTraverse:
            - gets all specified properties
            - parse the content of each property and extract links
            - save results into a dictionary like {'obj_url':[list_of_links]}
        """
        object_checked = self.unrestrictedTraverse(context, None)
        if object_checked is None:
            return {}, 0
        links = self.getLinksFromOb(object_checked, properties)
        return {object_checked.absolute_url(1): links}, len(links)

    security.declarePrivate('getLinksFromOb')
    def getLinksFromOb(self, ob, properties=None):
        """Return a list of links contained in the properties of ob.

            @param ob: object to check
            @param properties: properties to check;
                               if None all the properties of the
                               object's meta_type are checked
            @rtype: list
            @return: links contained in the properties of ob
        """
        def strip_hash(link):
            return link.split('#', 1)[0]

        all_links = []
        if properties is None:
            properties = self.getPropertiesMeta(ob.meta_type)
        for property, multilingual, islink in properties:
            values = []
            #check if the property is multiligual
            if multilingual:
                try:
                    for lang in self.gl_get_languages():
                        values.append((ob.getLocalProperty(property, lang), lang))
                except:
                    pass #Invalid property
            else:
                try:
                    values.append((getattr(ob, property), None))
                except:
                    pass #Invalid property
            for value, lang in values:
                if not value:
                    continue
                if islink:
                    # Skip default value for some fields
                    if value == 'http://':
                        continue
                    all_links.append( (strip_hash(value), property, lang) )
                else:
                    try:
                        try:
                            links = list(get_links_from_html(value))
                        except UnicodeError, err:
                            LOG('NaayaLinkChecker', DEBUG, 'an exception was raised when parsing property %s (lang %s) of %s : %s' % (property, lang, ob.absolute_url(1), err))
                            if isinstance(value, str):
                                safe_value = value.decode('utf-8', 'ignore')
                            else:
                                safe_value = value.encode('ascii', 'ignore')
                            links = list(get_links_from_html(safe_value))
                    except Exception, err: # invalid html, unicode errors etc.
                        LOG('NaayaLinkChecker', DEBUG, 'an exception was raised when parsing property %s (lang %s) of %s : %s' % (property, lang, ob.absolute_url(1), err))
                        links = get_links_from_text(value)
                    all_links.extend((strip_hash(x), property, lang)
                                      for x in links)
        return all_links

    security.declarePrivate('verifyIP')
    def verifyIP(self, REQUEST=None):
        """ verify IP """
        if not REQUEST or not REQUEST.has_key('REMOTE_ADDR'):
            raise AttributeError, "No REQUEST"
        if REQUEST['REMOTE_ADDR'] != self.ip_address.strip():
            raise Unauthorized

    security.declareProtected(view, 'automaticCheck')
    def automaticCheck(self, REQUEST=None):
        """ extract the urls from the objects,
            verify them and save the results for the broken links found in a log file
        """
        self.verifyIP(REQUEST)
        urlsinfo, total = self.processObjects()
        log_entries, all_urls = self.checkLinks(urlsinfo, total)
        self.manage_addLogEntry(self.REQUEST.AUTHENTICATED_USER.getUserName(), time.localtime(), log_entries)

    security.declarePrivate('cronCheck')
    def cronCheck(self):
        urlsinfo, total = self.processObjects()
        log_entries, all_urls = self.checkLinks(urlsinfo, total)
        self.manage_addLogEntry('_cron', time.localtime(), log_entries)

    security.declareProtected('Run Manual Check', 'manualCheck')
    def manualCheck(self, limit=0):
        """ extract the urls from the objects,
            verify them and return the results for the broken links found
        """
        urlsinfo, total = self.processObjects(limit)
        log_entries, all_urls = self.checkLinks(urlsinfo, total)
        now = time.localtime()
        self.manage_addLogEntry(self.REQUEST.AUTHENTICATED_USER.getUserName(),
                                now, log_entries)
        self.last_update = now
        return log_entries, all_urls

    security.declareProtected('Run Manual Check', 'manualCheck')
    def objectCheck(self, properties=[], context=''):
        """ extract the urls from the given object,
            verify it and return the results for the broken links found
        """
        urlsinfo, total = self.processObject(properties, context)
        return self.checkLinks(urlsinfo, total)

    security.declarePrivate('checkLinks')
    def checkLinks(self, urlsinfo, urlsnumber):
        #build a list with all links
        external_links = Set()
        internal_links = []
        for ob_url, val in urlsinfo.items():
            for v in val:
                link = v[0]
                if is_absolute_url(link):
                    external_links.add(link)
                else:
                    url = urlparse.urljoin(ob_url, link)
                    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
                    internal_links.append((link, urllib.unquote(path)))
        external_links = iter2Queue(external_links)
        #start threads
        LOG('NaayaLinkChecker', INFO, 'Starting %u link checking threads' % THREAD_COUNT)
        logresults = {}
        threads = []
        for thread in range(THREAD_COUNT):
            th = CheckerThread(external_links, logresults, proxy=self.proxy)
            th.setName(thread)
            threads.append(th)
            results = th.start()
        self.checkInternalLinks(internal_links, logresults)
        for thread in threads:
            thread.join()
        LOG('NaayaLinkChecker', INFO, 'Link checking threads stopped')
        return self.prepareLog(urlsinfo, logresults, urlsnumber, 0)

    security.declarePrivate('checkInternalLinks')
    def checkInternalLinks(self, links, logresults):
        for link, path in links:
            try:
                # unrestrictedTraverse would start at app root with a leading '/'
                doc  = self.unrestrictedTraverse(str(path).lstrip('/'), None)
            except:
                doc = None
            if doc is None:
                logresults[link] = '404: Not Found'
            else:
                logresults[link] = 'OK'

    security.declarePrivate('prepareLog')
    def prepareLog(self, links_dict, logresults, all_urls, manual=0):
        """ """
        log = []
        for ob_url, links in links_dict.items():
            ob = self.unrestrictedTraverse(urlparse.urlsplit(ob_url)[2])
            buf = []
            for link in links:
                err = logresults.get(link[0], 'NOT CHECKED')
                if err not in ('OK', 'NOT CHECKED'):
                    buf.append((link[0], err, link[1], link[2]))
            if buf:
                log.append((ob.getId(), ob.meta_type, ob.absolute_url(1), ob.icon, buf))
        return log, all_urls

    security.declareProtected(view_management_screens, 'getProperties')
    def getLastUpdate(self):
        """ Get the latest time.localtime
        Usecase:
            Can be used in ajax requests to check if an update has been
            finished
        """
        return getattr(self, 'last_update', '')

    security.declareProtected(view_management_screens, 'getProperties')
    def getProperties(self, metatype):
        """Get all added meta types"""
        return [p[0] for p in self.objectMetaType[metatype]]

    security.declareProtected(view_management_screens, 'getPropertiesMeta')
    def getPropertiesMeta(self, metatype):
        """Get all added meta types"""
        return self.objectMetaType[metatype]

    security.declareProtected(view_management_screens, 'hasMetaType')
    def hasMetaType(self, meta_type):
        """Is this meta_type in our list"""
        return self.objectMetaType.has_key(meta_type)

    security.declareProtected(view_management_screens, 'getObjectMetaTypes')
    def getObjectMetaTypes(self):
        """Get all added meta types"""
        return self.objectMetaType.keys()

    security.declareProtected(view_management_screens, 'manage_delProperty')
    def manage_delProperty(self, REQUEST=None):
        """Delete properties for a meta type"""
        editmetatype = REQUEST.get('editmetatype', '')
        delobjectproperty = REQUEST.get('objectProperty', [])
        if self.hasMetaType(editmetatype):
            # valid meta type - add property
            listproperties = self.objectMetaType[editmetatype]
            for property in self.umConvertToList(delobjectproperty):
                for prop_meta in listproperties:
                    if property == prop_meta[0]:
                        listproperties.remove(prop_meta)
                        break
            self.objectMetaType[editmetatype] = listproperties
            self._p_changed = 1
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('manage_properties?editmetatype=' + self.umURLEncode(editmetatype) + '#property')

    security.declareProtected(view, 'getLogEntries')
    def getLogEntries(self):
        """Returns a list with all 'LogEntry' objects"""
        return self.objectValues('LogEntry')

    security.declareProtected(view, 'getFailPercentage')
    def getFailPercentage(self, link):
        """Returns the link fail percentage based on the last 5 logs"""
        logs = self.getLogEntries()
        logs.sort(lambda x, y: cmp(y.bobobase_modification_time(), x.bobobase_modification_time()))
        logs = logs[:5]
        failed = 0
        for log in logs:
            for entry in log.url_list:
                for url in entry[4]:
                    try:
                        if force_to_unicode(url[0]) == force_to_unicode(link):
                            failed += 1
                            continue
                    except UnicodeDecodeError:
                        continue
        rate = int(((failed * 1.0) / len(logs)) * 100)
        if rate > 100:
            return 100
        return rate

    manage_addLogEntry = LogEntry.manage_addLogEntry

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties')
    manage_properties = PageTemplateFile("zpt/LinkChecker_edit", globals())

    manage_main = folder_manage_main_plus
    ny_before_listing = PageTemplateFile('zpt/LinkChecker_manage_main_header', globals())

    #site pages
    security.declareProtected(view, 'manual_check_html')
    manual_check_html = PageTemplateFile("zpt/LinkChecker_manual", globals())

    security.declareProtected(view, 'style_html')
    style_html = PageTemplateFile("zpt/LinkChecker_style", globals())

    security.declareProtected(view, 'log_html')
    log_html = PageTemplateFile("zpt/LinkChecker_log", globals())

    security.declareProtected(view, 'view_log')
    view_log = PageTemplateFile("zpt/LinkChecker_logForm",globals())

InitializeClass(LinkChecker)
