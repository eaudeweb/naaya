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

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

manage_addLocalChannelForm = PageTemplateFile('zpt/localchannel_manage_add', globals())
def manage_addLocalChannel(self, id='', title='', description='', language=None, type='',
    objmetatype=[], numberofitems='', portlet='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if language is None: language = self.gl_get_selected_language()
    if not id: id = PREFIX_SUFIX_LOCALCHANNEL % (self.utGenRandomId(6), language)
    objmetatype = self.utConvertToList(objmetatype)
    try: numberofitems = abs(int(numberofitems))
    except: numberofitems = 0
    ob = LocalChannel(id, title, description, language, type, objmetatype, numberofitems)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_localchannel(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class LocalChannel(SimpleItem, utils):
    """ """

    meta_type = METATYPE_LOCALCHANNEL
    icon = 'misc_/NaayaCore/LocalChannel.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'View', 'action': 'index_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, language, type, objmetatype, numberofitems):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.objmetatype = objmetatype
        self.numberofitems = numberofitems

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.delete_portlet_for_object(item)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        l_rdf = []
        l_rdf.append('<item rdf:about="%s">' % self.absolute_url())
        l_rdf.append('<link>%s</link>' % self.absolute_url())
        l_rdf.append('<dc:title>%s</dc:title>' % self.utXmlEncode(self.title_or_id()))
        l_rdf.append('<dc:identifier>%s</dc:identifier>' % self.absolute_url())
        l_rdf.append('<dc:description>%s</dc:description>' % self.utXmlEncode(self.description))
        l_rdf.append('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(self.contributor))
        l_rdf.append('<dc:language>%s</dc:language>' % self.utXmlEncode(self.language))
        l_rdf.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(self.creator))
        l_rdf.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(self.publisher))
        l_rdf.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(self.rights))
        l_rdf.append('<dc:type>%s</dc:type>' % self.utXmlEncode(self.get_channeltype_title(self.type)))
        l_rdf.append('<dc:format>text/xml</dc:format>')
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(self.publisher))
        l_rdf.append('</item>')
        return ''.join(l_rdf)

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language=None, type='', objmetatype=[], numberofitems='', REQUEST=None):
        """ """
        if language is None: language = self.gl_get_selected_language()
        objmetatype = self.utConvertToList(objmetatype)
        try: numberofitems = abs(int(numberofitems))
        except: numberofitems = 0
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.objmetatype = objmetatype
        self.numberofitems = numberofitems
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_properties_html')

    def get_objects_for_rdf(self):
        #return the objects to be syndicated
        l_items = []
        if len(self.objmetatype)>0:
            l_howmany = -1
            if self.numberofitems != 0:
                l_howmany = self.numberofitems
            l_items = self.query_translated_objects(meta_type=self.objmetatype, lang=self.language, approved=1, howmany=l_howmany)
        return l_items

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        l_site = self.getSite()
        lang = self.language
        l_items = self.get_objects_for_rdf()
        l_rdf = []
        l_rdf.append('<?xml version="1.0" encoding="utf-8"?>')
        l_rdf.append('<rdf:RDF %s>' % self.getNamespacesForRdf())
        l_rdf.append('<channel rdf:about="%s">' % l_site.absolute_url())
        l_rdf.append('<title>%s</title>' % self.utXmlEncode(self.title))
        l_rdf.append('<link>%s</link>' % l_site.absolute_url())
        l_rdf.append('<description>%s</description>' % self.utXmlEncode(self.description))
        l_rdf.append('<dc:identifier>%s</dc:identifier>' % l_site.absolute_url())
        l_rdf.append('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.utGetTodayDate()))
        l_rdf.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        l_rdf.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        l_rdf.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(l_site.getLocalProperty('site_title', lang)))
        l_rdf.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(l_site.getLocalProperty('site_subtitle', lang)))
        l_rdf.append('<dc:language>%s</dc:language>' % self.utXmlEncode(lang))
        l_rdf.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(l_site.getLocalProperty('rights', lang)))
        l_rdf.append('<dc:type>%s</dc:type>' % self.utXmlEncode(self.type))
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        l_rdf.append('<items>')
        l_rdf.append('<rdf:Seq>')
        for l_item in l_items:
            l_rdf.append('<rdf:li resource="%s"/>' % l_item.absolute_url())
        l_rdf.append('</rdf:Seq>')
        l_rdf.append('</items>')
        l_rdf.append('</channel>')
        if self.hasImage():
            l_rdf.append('<image>')
            l_rdf.append('<title>%s</title>' % self.utXmlEncode(self.title))
            l_rdf.append('<url>%s</url>' % self.getImagePath())
            l_rdf.append('<link>%s</link>' % l_site.absolute_url())
            l_rdf.append('<description>%s</description>' % self.utXmlEncode(self.description))
            l_rdf.append('</image>')
        for l_item in l_items:
            l_rdf.append(l_item.syndicateThis(lang))
        l_rdf.append("</rdf:RDF>")
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return ''.join(l_rdf)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/localchannel_properties', globals())

InitializeClass(LocalChannel)
