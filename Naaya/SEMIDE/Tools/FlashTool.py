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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania

#Python imports
from os.path import join
import re

#Zope imports
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view, manage_users
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Naaya imports
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.NaayaCore.managers.utils import utils, tmpfile
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyDocument.NyDocument import addNyDocument
from Products.NaayaCore.ProfilesTool.ProfileMeta import ProfileMeta
from Products.NaayaCore.managers.paginator import ObjectPaginator

#SEMIDE imports
from Products.SEMIDE.constants import *
from FlashTemplate import manage_addFlashTemplateForm, manage_addFlashTemplate
from converters.xslt import Converter
from mdh.MDH import MDH


def manage_addFlashTool(self, REQUEST=None):
    """ add a flash tool """
    ob = FlashTool(ID_FLASHTOOL, TITLE_FLASHTOOL)
    self._setObject(ID_FLASHTOOL, ob)
    obj = self._getOb(ID_FLASHTOOL)
    obj.path = self.getSitePath(1)
    obj.loadDefaultData()
    obj._p_changed = 1
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class FlashTool(Folder, ProfileMeta, utils):
    """ FlashTool class """

    meta_type = FLASHTOOL_METATYPE
    icon = 'misc_/SEMIDE/FlashTool.gif'


    security = ClassSecurityInfo()

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Settings', 'action': 'manage_settings_html'},
        )
        +
        Folder.manage_options[3:]
    )

    meta_types = (
                {'name': FLASHTEMPLATE_METATYPE, 'action': 'manage_addFlashTemplateForm'},
                )
    all_meta_types = meta_types


    def __init__(self, id, title):
        """ constructor """

        self.id = id
        self.title = title
        self.langs = []
        self.archive_path = 'publications/eflash'
        self.path = ''

        self.df_template = 'monthly'
        self.news_start_date = self.utGetTodayDate()
        self.news_end_date = self.news_start_date + 30
        self.event_start_date = self.utGetTodayDate()
        self.event_end_date = self.event_start_date + 30
        self.doc_start_date = self.utGetTodayDate()
        self.doc_end_date = self.doc_start_date + 30

        self.notif_date = self.utGetTodayDate() + 30
        self.notif_admin = 1
        self.lastflashdate = self.utStringDate(self.notif_date)
        self.uploadmetatypes = [METATYPE_NYFILE, METATYPE_NYSEMTEXTLAWS]
        self.notif_cache = []


    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ load the default templates """
        self.langs = list(self.gl_get_languages())
        try:
            manage_addFlashTemplate(self, 'monthly', 'Template for monthly eFlash')
            manage_addFlashTemplate(self, 'instant', 'Template for instant eFlash', notif_type='instant')
        except UnicodeDecodeError:
            pass


    ########## ZMI #################
    security.declareProtected(view_management_screens, 'manageSettings')
    def manageSettings(self, title='', path='', archive_path='', news_sd='', news_ed='', event_sd='', event_ed='', doc_sd='', 
        doc_ed='', notif_date='', notif_admin='', uploadmetatypes=[], langs=[], REQUEST=None):
        """ manage properties """
        self.title = title
        self.path = path
        self.archive_path = archive_path
        self.news_start_date = self.utConvertStringToDateTimeObj(news_sd)
        self.news_end_date = self.utConvertStringToDateTimeObj(news_ed)
        self.event_start_date = self.utConvertStringToDateTimeObj(event_sd)
        self.event_end_date = self.utConvertStringToDateTimeObj(event_ed)
        self.doc_start_date = self.utConvertStringToDateTimeObj(doc_sd)
        self.doc_end_date = self.utConvertStringToDateTimeObj(doc_ed)
        self.notif_date = self.utConvertStringToDateTimeObj(notif_date)
        self.lastflashdate = self.utStringDate(self.notif_date)
        try: self.notif_admin = int(notif_admin)
        except: self.notif_admin = 1
        self.uploadmetatypes = self.utConvertLinesToList(uploadmetatypes)
        self.langs = self.utConvertLinesToList(langs)
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_settings_html?save=ok')

    ########## API #################
    security.declareProtected(view_management_screens, 'testLocation')
    def testLocation(self):
        """ """
        return self.unrestrictedTraverse(self.archive_path, None)

    security.declarePrivate('addfornotif_object')
    def addfornotif_object(self, ob):
        """
        Cache info about the given object for instant notification.
        @param ob: the object
        @type ob: naaya object instance
        """
        if ob.meta_type in self.uploadmetatypes:
            #this meta type is set for instant notification
            ob_path = ob.absolute_url(1)
            if ob_path.find(self.absolute_url(1)) != 0:
                #test not to be an object created inside FlashTool
                if ob_path.find(self.path) == 0:
                    #the object path matches the FlashTool path
                    #put the object in cache
                    if not ob_path in self.notif_cache:
                        self.notif_cache.append(ob_path)
            self._p_changed = 1

    security.declarePrivate('delfornotif_object')
    def delfornotif_object(self, ob):
        """
        Remove from instant notification's cache info about the given object.
        @param ob: the object
        @type ob: naaya object instance
        """
        if ob.meta_type in self.uploadmetatypes:
            #this meta type is set for instant notification
            ob_path = ob.absolute_url(1)
            if ob_path.find(self.path) == 0:
                #the object path matches the FlashTool path
                #remove the object from cache
                try: self.notif_cache.remove(ob_path)
                except: pass
            self._p_changed = 1

    #security.declarePrivate('emptyNotifCache')
    def emptyNotifCache(self):
        """
        Empty instant notification's cache.
        """
        self.notif_cache = []
        self._p_changed = 1

    security.declarePrivate('add_uploadmetatype')
    def add_uploadmetatype(self, m):
        """
        Add a new upload meta types to list.
        @param l: object meta type
        @type l: string
        """
        if m not in self.uploadmetatypes:
            self.uploadmetatypes.append(m)
            self._p_changed = 1

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getFlashDocument')
    def getFlashDocument(self, type):
        """
        Returns the generated document inside archives
        """
        return self.getFlashArchive()._getOb('%s_%s' % (self.lastflashdate, type), None)

    security.declarePrivate('_ getFlashUsers')
    def _getFlashUsers(self, query=''):
        site = self.getSite()
        profiles_tool = site.getProfilesTool()
        users = []
        users_a = users.append
        for user in site.getAuthenticationTool().getUsers():
            profile = profiles_tool.getProfile(user.name)
            sheet_ob = profile.getSheetById(self.getInstanceSheetId())
            if sheet_ob.notify or sheet_ob.flash:
                if query:
                    if self.utToUnicode(user.name).find(query)!=-1 or user.email.find(query)!=-1 or \
                            self.utToUnicode(user.firstname).find(query)!=-1 or self.utToUnicode(user.lastname).find(query)!=-1:
                        users_a((user.name, user.firstname, user.lastname, user.email, sheet_ob.notify, sheet_ob.language, sheet_ob.flash))
                else:
                    users_a((user.name, user.firstname, user.lastname, user.email, sheet_ob.notify, sheet_ob.language, sheet_ob.flash))
        return users

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getFlashUsers')
    def getFlashUsers(self, query='', skey=0, rkey=''):
        """
            return the users list
        """
        if skey == 'name':  skey = 0
        elif skey == 'fn':  skey = 1
        elif skey == 'ln':  skey = 2
        elif skey == 'email':   skey = 3
        elif skey == 'instant':  skey = 4
        elif skey == 'lang':    skey = 5
        else:   skey = 0
        users = self._getFlashUsers(query)
        results = [(x[skey], x) for x in users]
        results.sort()
        if rkey: results.reverse()
        return ObjectPaginator([val for (key, val) in results], num_per_page=15, orphans=5)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'exportFlashUsers')
    def exportFlashUsers(self, REQUEST=None, RESPONSE=None):
        """ """
        data = [('Username', 'Firstname', 'Lastname', 'Email', 'Instant notification', 'Language', 'Monthly eFlash')]
        data_app = data.append
        for user in self._getFlashUsers():
            data_app((user[0], self.utToUtf8(user[1]), self.utToUtf8(user[2]), user[3], user[4], self.gl_get_language_name(user[5]), user[6]))
        tmp_name = tmpfile(data)
        content = open(str(tmp_name)).read()
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % 'flashusers.csv')
        return content

    security.declarePrivate('emailUsers')
    def emailUsers(self, subject, body):
        """
        Send an email to all users subscribed to given category.
        """
        mdh_ob = MDH()
        site = self.getSite()
        for user, fname, lname, email, instant, lang in self.getFlashUsers():
            mdh_ob.sendFlashEmail(body, body, email, site.mail_address_from, subject)

    security.declarePrivate('is_arabic')
    def is_arabic(self, lang):
        """ test if arabic language """
        return lang in ['ar']

    security.declarePrivate('clean_duplicates')
    def clean_duplicates(self, p_list):
        """Eliminate duplicates from a list"""
        dict = {}
        for item in p_list:
            dict[item] = ""
        return dict.keys()

    security.declarePrivate('collect_objects')
    def collect_objects(self, path=''):
        """ search the catalog to find objects for a given date interval """
        news = self.getCatalogedObjects(meta_type=[METATYPE_NYSEMNEWS], 
                                            approved=1, 
                                            resource_date=self.news_start_date, 
                                            resource_date_range='min',
                                            path=path)
        events = self.getCatalogedObjects(meta_type=[METATYPE_NYSEMEVENT], 
                                            approved=1, 
                                            resource_date=self.event_start_date, 
                                            resource_date_range='min',
                                            path=path)

        documents = self.getCatalogedObjects(meta_type=[METATYPE_NYSEMDOCUMENT], 
                                            approved=1, 
                                            resource_date=self.doc_start_date, 
                                            resource_date_range='min',
                                            path=path)

        results = [obj for obj in news if obj.news_date <= self.news_end_date]
        results.extend([obj for obj in events if obj.start_date <= self.event_end_date])
        results.extend([obj for obj in documents if obj.releasedate <= self.doc_end_date])
        return results

    security.declarePrivate('filter_objects')
    def filter_objects(self, objects):
        """ filter the objects """
        inbrief, nomination, publication, tender, papers, training, events = [], [], [], [], [], [], []
        for obj in objects:
            if obj.meta_type == METATYPE_NYSEMNEWS:
                if obj.news_type == INBRIEF:
                    inbrief.append(obj)
                if obj.news_type == NOMINATION or obj.news_type == VACANCIES:
                    nomination.append(obj)
                if obj.news_type == TENDERS or obj.news_type == CALLFORPROPOSALS:
                    tender.append(obj)
                if obj.news_type == PAPERS:
                    papers.append(obj)
            if obj.meta_type == METATYPE_NYSEMEVENT:
                if obj.event_type == TRAINING:
                    training.append(obj)
                else:
                    events.append(obj)
            if obj.meta_type == METATYPE_NYSEMDOCUMENT:
                publication.append(obj)
        inbrief = self.utSortObjsListByAttr(inbrief, 'news_date')
        nomination = self.utSortObjsListByAttr(nomination, 'news_date')
        tender = self.utSortObjsListByAttr(tender, 'news_date')
        papers = self.utSortObjsListByAttr(papers, 'news_date')
        training = self.utSortObjsListByAttr(training, 'start_date')
        events = self.utSortObjsListByAttr(events, 'start_date')
        publication = self.utSortObjsListByAttr(publication, 'resource_date')
        return inbrief, nomination, publication, tender, papers, training, events

    security.declarePrivate('generate_flash')
    def generate_flash(self):
        """ """
        notifications = self.collect_objects(self.path)
        inbrief, nomination, publication, tender, papers, training, events = self.filter_objects(notifications)
        if inbrief or nomination or publication or tender or papers or training or events:
            results_html = self.generate_xml(inbrief, nomination, publication, tender, papers, training, events, self.langs, 'html')
            results_text = self.generate_xml(inbrief, nomination, publication, tender, papers, training, events, self.langs, 'text')
            self.save_flash(results_html, 'html')
            self.save_flash(results_text, 'text')
            return True
        return False

    security.declarePrivate('save_flash')
    def save_flash(self, results, p_type):
        """ """
        template = self._getOb(self.df_template)
        archive = self.getFlashArchive()
        #create mail document
        id = '%s_%s' % (self.lastflashdate, p_type)
        doc_obj = archive._getOb(id, None)
        if doc_obj is None:
            addNyDocument(archive, id=id, title='', body='')
            doc_obj = archive._getOb(id, None)
            doc_obj.approveThis(0, None)
            doc_obj.submitThis()
        for k in results.keys():
            style = template._getOb("%s_%s" % (p_type, k)).document_src()
            x = self.render_xml(results[k], style)
            doc_obj.saveProperties(title='Flash to be sent on %s (%s version)' % (self.utShowDateTime(self.notif_date), p_type), body=x, lang=k)

    security.declarePrivate('render_xml')
    def render_xml(self, xml, xslt):
        """ """
        conv = Converter()
        return unicode(conv(xml, xslt), 'utf-8').replace('<?xml version="1.0"?>', '')

    security.declarePrivate('generate_xml')
    def generate_xml(self, inbrief, nomination, publication, tender, papers, training, events, langs, mesg_type='html'):
        """ """
        results = {}
        for lang in langs:
            xml = []
            xml_append = xml.append
            xml_append('<?xml version="1.0" encoding="UTF-8"?>')
            xml_append('<eflash>')
            xml_append('<title>%s</title>' % self.utXmlEncode(self.title))
            xml_append('<lang>%s</lang>' % lang)
            xml_append('<isrtl>%s</isrtl>' % self.is_arabic(lang))
            xml_append('<description>%s</description>' % self.utXmlEncode(self.title))
            xml_append('<portal_url>%s</portal_url>' % self.utXmlEncode(self.getSitePath()))
            xml_append('<sections>')

            #headline section
            xml_append('<section id="headline">')
            xml_append('</section>')

            #in brief section
            if inbrief:
                xml_append('<section id="inbrief">')
                for obj in inbrief:
                    if obj.istranslated(lang):
                        xml_append('<news title="%s" source="%s" source_link="%s" file_link="%s" url="%s" lang="%s" isrtl="%s">' %
                        (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.getLocalProperty('source', lang)), \
                        self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), self.utXmlEncode(obj.absolute_url(0)), \
                        lang, self.is_arabic(lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</news>')
                xml_append('</section>')

            #nominations & vacancies section
            if nomination:
                xml_append('<section id="nominations">')
                for obj in nomination:
                    if obj.istranslated(lang):
                        xml_append('<news title="%s" source="%s" source_link="%s" file_link="%s" url="%s" lang="%s" isrtl="%s">' % 
                        (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.getLocalProperty('source', lang)), \
                        self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), self.utXmlEncode(obj.absolute_url(0)), \
                        lang, self.is_arabic(lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</news>')
                xml_append('</section>')

            #publications section
            if publication:
                xml_append('<section id="publications">')
                for obj in publication:
                    if obj.istranslated(lang):
                        xml_append('<document title="%s" source="%s" source_link="%s" file_link="%s" publisher="%s" url="%s" lang="%s" isrtl="%s">' % 
                        (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.getLocalProperty('source', lang)), \
                        self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), self.utXmlEncode(obj.publisher), self.utXmlEncode(obj.absolute_url(0)), \
                        lang, self.is_arabic(lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</document>')
                xml_append('</section>')

            #call for tenders and proposal section
            if tender:
                xml_append('<section id="proposal">')
                for obj in tender:
                    if obj.istranslated(lang):
                        xml_append('<news title="%s" source="%s" source_link="%s" file_link="%s" url="%s" lang="%s" isrtl="%s">' % 
                        (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.getLocalProperty('source', lang)), \
                        self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), self.utXmlEncode(obj.absolute_url(0)), \
                        lang, self.is_arabic(lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</news>')
                xml_append('</section>')

            #call for papers section
            if papers:
                xml_append('<section id="papers">')
                for obj in papers:
                    if obj.istranslated(lang):
                        xml_append('<news title="%s" source="%s" source_link="%s" file_link="%s" url="%s" lang="%s" isrtl="%s">' % 
                        (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.getLocalProperty('source', lang)), \
                        self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), self.utXmlEncode(obj.absolute_url(0)), \
                        lang, self.is_arabic(lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</news>')
                xml_append('</section>')

            #training section
            if events:
                xml_append('<section id="training">')
                for obj in training:
                    if obj.istranslated(lang):
                        xml_append('<event title="%s" start_date="%s" end_date="%s" source="%s" source_link="%s" file_link="%s" url="%s" lang="%s" isrtl="%s">' %
                            (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.start_date), self.utXmlEncode(obj.end_date), \
                            self.utXmlEncode(obj.getLocalProperty('source', lang)), self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), \
                            self.utXmlEncode(obj.absolute_url(0)), lang, self.is_arabic(lang)))
                        xml_append('<address>%s</address>' % self.utXmlEncode(obj.getLocalProperty('address', lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</event>')
                xml_append('</section>')

            #events section
            if events:
                xml_append('<section id="events">')
                for obj in events:
                    if obj.istranslated(lang):
                        xml_append('<event title="%s" start_date="%s" end_date="%s" source="%s" source_link="%s" file_link="%s" url="%s" lang="%s" isrtl="%s">' %
                            (self.utXmlEncode(obj.getLocalProperty('title', lang)), self.utXmlEncode(obj.start_date), self.utXmlEncode(obj.end_date), \
                            self.utXmlEncode(obj.getLocalProperty('source', lang)), self.utXmlEncode(obj.source_link), self.utXmlEncode(obj.file_link), \
                            self.utXmlEncode(obj.absolute_url(0)), lang, self.is_arabic(lang)))
                        xml_append('<address>%s</address>' % self.utXmlEncode(obj.getLocalProperty('address', lang)))
                        if mesg_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(obj.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(obj.getLocalProperty('description', lang))))
                        xml_append('</event>')
                xml_append('</section>')

            #footer section
            #xml_append('<section id="footer">')
            #xml_append('</section')

            xml_append('</sections>')
            xml_append('</eflash>')
            results[lang] = ''.join(xml)
        return results

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'runTrigger')
    def runTrigger(self, REQUEST=None):
        """ 
        Trigger the monthly notification
        """
        uid = self.get_site_uid()
        self.mainTrigger(uid, now=1)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/admin_flash_notification_html?sent=1' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'testTrigger')
    def testTrigger(self, REQUEST=None):
        """ """
        uid = self.get_site_uid()
        self.instantTrigger(uid)

    #methods to be runned by OS scheduler - crond
    def instantTrigger(self, uid):
        """
        Used by cron tools to trigger instant notification.

        @param uid: site uid
        @type uid: string
        """
        if uid==self.get_site_uid():
            htmls = {}
            if self.notif_cache:
                #grab all the items
                self.notif_cache = self.clean_duplicates(self.notif_cache)
                #get the objects
                items_obj = []
                for item in self.notif_cache:
                    try:
                        items_obj.append(self.unrestrictedTraverse(item))
                    except KeyError:
                        pass
                xmls_html = self.instant_xml(items_obj, 'html')
                xmls_text = self.instant_xml(items_obj, 'text')
                htmls = {}
                for lang, xml in xmls_html.items():
                    #generate htmls
                    htmls[lang] = [self.instant_html(xml, 'html', lang)]
                for lang, xml in xmls_text.items():
                    #generate texts
                    htmls[lang].append(self.instant_html(xml, 'text', lang))
                #send notifications
                if htmls:
                    #at least one item
                    mdh_ob = MDH()
                    site = self.getSite()
                    authtool_ob = site.getAuthenticationTool()

                    for profile in site.getProfilesTool().getProfiles():
                        sheet_ob = profile.getSheetById(self.getInstanceSheetId())
                        if sheet_ob.notify == 1:
                            #the user wants to receive instant notification
                            if sheet_ob.language in htmls.keys():
                                #get user
                                user = authtool_ob.getUser(profile.id)
                                #send email
                                html, text = htmls[sheet_ob.language]
                                mdh_ob.sendFlashEmail(html, text, 'cornel.nitu@eaudeweb.ro', site.mail_address_from, 'SEMIDE eFlash instant notification')
                    #clear cache
                    self.emptyNotifCache()
            return "e-Flash notification sent successfully"


    security.declareProtected(view, 'mainTrigger')
    def mainTrigger(self, uid, now=0):
        """
        Used by cron tools to trigger the eFlash notification.

        @param uid: site uid
        @type uid: string
        """
        if uid==self.get_site_uid():
            archive = self.getFlashArchive()
            #check if this is the notification day
            today = self.utGetTodayDate()
            if (today.year() == self.notif_date.year() and \
                today.month() == self.notif_date.month() and \
                today.day() == self.notif_date.day()) or now:
                #start sending eFlash
                d = {}
                mdh_ob = MDH()
                site = self.getSite()
                auth_tool = site.getAuthenticationTool()
                for profile in site.getProfilesTool().getProfiles():
                    sheet_ob = profile.getSheetById(self.getInstanceSheetId())
                    if sheet_ob.language in self.langs:
                        #get user
                        user = auth_tool.getUser(profile.id)
                        if archive is not None:
                            try:
                                #get eFlash documents
                                html = archive._getOb('%s_html' % self.lastflashdate).getLocalProperty('body', sheet_ob.language)
                                text = archive._getOb('%s_text' % self.lastflashdate).getLocalProperty('body', sheet_ob.language)
                            except AttributeError:
                                if self.generate_flash():
                                    #get eFlash documents
                                    html = archive._getOb('%s_html' % self.lastflashdate).getLocalProperty('body', sheet_ob.language)
                                    text = archive._getOb('%s_text' % self.lastflashdate).getLocalProperty('body', sheet_ob.language)
                            try:
                                #send email
                                mdh_ob.sendFlashEmail(html, text, user.email, site.mail_address_from, self.title)
                            except:
                                pass
                #approve the html version of the eFlash
                try:
                    mesg = archive._getOb('%s_html' % self.lastflashdate)
                    mesg.title = 'Flash sent on %s' % self.utShowDateTime(self.utGetTodayDate())
                    mesg.approveThis()
                except AttributeError:
                    pass
                #delete the text version of the eFlash
                try:
                    archive.manage_delObjects('%s_text' % self.lastflashdate)
                except:
                    pass
                #update parameters

                #increment the news interval
                self.news_start_date = self.notif_date
                self.news_end_date = self.notif_date + 30

                #increment the event interval
                self.event_start_date = self.notif_date
                self.event_end_date = self.notif_date + 30

                #increment the documents interval
                self.doc_start_date = self.notif_date
                self.doc_end_date = self.notif_date + 30

                #increment the notification date
                self.notif_date = self.notif_date + 30

                self._p_changed = 1
            else:
                #check for admin notification date
                notif_admin_date = self.notif_date - self.notif_admin
                if today.year() == notif_admin_date.year() and \
                    today.month() == notif_admin_date.month() and \
                    today.day() == notif_admin_date.day():
                    #send email to administrator
                    #step 1: generate eFlash
                    self.generate_flash()
                    #step 2: send email
                    self.adminNotification()
            return "e-Flash notification sent successfully"

    security.declareProtected(view, 'adminNotification')
    def adminNotification(self):
        """ """
        site = self.getSite()
        emailtool_ob = self.getEmailTool()
        email_template = emailtool_ob._getOb('email_flashnotif')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@PORTAL_TITLE@@', site.site_title)
        l_content = l_content.replace('@@PORTAL_URL@@', site.absolute_url())
        l_content = l_content.replace('@@EFLASH_URL@@', '%s/admin_flash_preview_html' % site.absolute_url())
        l_content = l_content.replace('@@NOTIF_DATE@@', str(self.notif_date))
        emailtool_ob.sendEmail(l_content, site.administrator_email, site.mail_address_from, l_subject)

    #instant notification section start

    security.declarePrivate('instant_xml')
    def instant_xml(self, notifications, p_type='html'):
        """ 
            create the XML structure.
            notifications is a list: [items]
        """
        results = {}
        for lang in self.langs:
            xml = []
            xml_append = xml.append
            xml_append('<?xml version="1.0" encoding="UTF-8"?>')
            xml_append('<inotif lang="%s" isrtl="%s">' % (lang, self.is_arabic(lang)))
            xml_append('<objects>')
            flag = 0
            for item in notifications:
                if item.istranslated(lang):
                    flag = 1
                    xml_append('<object title="%s" url="%s" releasedate="%s">' % 
                        (self.utXmlEncode(item.getLocalProperty('title', lang)), \
                        self.utXmlEncode(item.absolute_url(0)), self.utXmlEncode(item.releasedate)))
                    if self.instant_is_folder(item):
                        xml_append('<description>%s</description>' % self.utXmlEncode(item.getLocalProperty('tooltip', lang)))
                    else:
                        if p_type == 'html':
                            xml_append('<description>%s</description>' % self.utXmlEncode(item.getLocalProperty('description', lang)))
                        else:
                            xml_append('<description>%s</description>' % self.utXmlEncode(self.utStripAllHtmlTags(item.getLocalProperty('description', lang))))
                    xml_append('</object>')
            xml_append('</objects>')
            xml_append('</inotif>')
            if flag:
                results[lang] = ''.join(xml)
        return results


    security.declarePrivate('get_instant_template')
    def get_instant_template(self, template='instant'):
        """ get the default template for instant notifications """
        return self._getOb(template, None)


    security.declarePrivate('instant_html')
    def instant_html(self, xml, p_type, lang):
        """ 
            generate mail 
        """
        template = self.get_instant_template()
        style = template._getOb("%s_%s" % (p_type, lang)).document_src()
        return self.render_xml(xml, style)

    security.declarePrivate('instant_is_folder')
    def instant_is_folder(self, item):
        """ check if is a folderish object """
        return item.meta_type in [METATYPE_FOLDER, METATYPE_NYCOUNTRY]

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_settings_html')
    manage_settings_html = PageTemplateFile('zpt/flash_settings', globals())

    #ProfileMeta implementation
    security.declarePrivate('loadProfileMeta')
    def loadProfileMeta(self):
        """
        Load profile metadata and updates existing profiles.
        """
        self._loadProfileMeta(join(SEMIDE_PRODUCT_PATH, 'Tools'))

    security.declareProtected(view, 'profilesheet')
    def profilesheet(self, name=None, flash='', language='', notify='', REQUEST=None,):
        """
        Updates the profile of the given user. Must be implemented.
        """
        if name is None: name = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if flash:   flash = 1
        else:   flash = 0
        if notify:  notify = 1
        else:   notify = 0
        self._profilesheet(name, {'flash': flash, 'language': language,
            'notify': notify})
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/profilesheet_html' % self.absolute_url())

    security.declareProtected(view, 'profilesheet_html')
    def profilesheet_html(self, REQUEST=None, RESPONSE=None):
        """
        View for instance associated sheet. Must be implemented.
        """
        return self.getFormsTool().getContent({'here': self}, 'flashtool_profilesheet')

    #site actions
    security.declareProtected(view, 'process_subscribe')
    def process_subscribe(self, firstname='', lastname='', email='', username='',
        password='', confirm='', flash='', language='', notify='',
        REQUEST=None):
        """ """
        #process form
        #validate data .....
        if flash:   flash = 1
        else:   flash = 0
        if notify: notify = 1
        else: notify = 0
        #create user
        msg = err = ''
        try:
            #create the user
            self.getAuthenticationTool().manage_addUser(username, password,
                confirm, [], [], firstname, lastname, email)
        except Exception, error:
            err = error
        else:
            #update user profile
            self.profilesheet(username, flash, language, notify)
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if msg != '':
                self.setSession('title', 'Thank you for subscribing')
                self.setSession('body', '')
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
            if err != '':
                self.setSessionErrors([err])
                REQUEST.RESPONSE.redirect('%s/subscribe_html' % self.absolute_url())

    #site pages
    security.declareProtected(view, 'subscribe_html')
    def subscribe_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'flashtool_subscribe')

InitializeClass(FlashTool)
