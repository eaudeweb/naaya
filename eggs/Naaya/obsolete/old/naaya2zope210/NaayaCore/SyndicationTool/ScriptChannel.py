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
from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PythonScripts.PythonScript import PythonScript
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.interfaces import IScriptChannel
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

manage_addScriptChannelForm = PageTemplateFile('zpt/scriptchannel_manage_add', globals())
def manage_addScriptChannel(self, id='', title='', description='', language=None, type='',
    body='', numberofitems='', portlet='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if language is None: language = self.gl_get_selected_language()
    if not id: id = PREFIX_SUFIX_SCRIPTCHANNEL % (self.utGenRandomId(6), language)
    try: numberofitems = abs(int(numberofitems))
    except: numberofitems = 0
    ob = ScriptChannel(id, title, description, language, type, numberofitems)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.write(body)
    if portlet:
        self.create_portlet_for_scriptchannel(ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class ScriptChannel(PythonScript, utils):
    """ """

    implements(IScriptChannel)

    meta_type = METATYPE_SCRIPTCHANNEL
    icon = 'misc_/NaayaCore/ScriptChannel.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
        )
        +
        (
            PythonScript.manage_options[0],
        )
        +
        PythonScript.manage_options[2:]
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, language, type, numberofitems):
        """ """
        PythonScript.__dict__['__init__'](self, id)
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.numberofitems = numberofitems

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        s = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra('<item rdf:about="%s">' % self.absolute_url())
        ra('<link>%s</link>' % self.absolute_url())
        ra('<title>%s</title>' % self.utXmlEncode(self.title_or_id()))
        ra('<description><![CDATA[%s]]></description>' % self.utToUtf8(self.description))
        ra('<dc:title>%s</dc:title>' % self.utXmlEncode(self.title_or_id()))
        ra('<dc:identifier>%s</dc:identifier>' % self.absolute_url())
        ra('<dc:description><![CDATA[%s]]></dc:description>' % self.utToUtf8(self.description))
        ra('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(self.contributor))
        ra('<dc:language>%s</dc:language>' % self.utXmlEncode(self.language))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(self.creator))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(self.publisher))
        ra('<dc:rights>%s</dc:rights>' % self.utXmlEncode(self.rights))
        ra('<dc:type>%s</dc:type>' % self.utXmlEncode(self.get_channeltype_title(self.type)))
        ra('<dc:format>text/xml</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.publisher))
        ra('</item>')
        return ''.join(r)

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language=None, type='', numberofitems='', REQUEST=None):
        """ """
        if language is None: language = self.gl_get_selected_language()
        try: numberofitems = abs(int(numberofitems))
        except: numberofitems = 0
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.numberofitems = numberofitems
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_properties_html')

    def get_objects_for_rdf(self):
        #return the objects to be syndicated
        return self._exec({'context': self, 'container': self}, {}, {})

    security.declareProtected(view, 'index_html')
    def index_html(self, feed='', REQUEST=None, RESPONSE=None):
        """ """
        
        if feed == 'atom':
            return self.syndicateAtom(self, self.get_objects_for_rdf(), self.language)
        
        s = self.getSite()
        lang = self.language
        if lang == 'auto':
            lang = self.gl_get_selected_language()
        l_items = self.get_objects_for_rdf()
        r = []
        ra = r.append
        ra('<?xml version="1.0" encoding="utf-8"?>')
        ra('<rdf:RDF %s>' % self.getNamespacesForRdf())
        ra('<channel rdf:about="%s">' % s.absolute_url())
        ra('<title>%s</title>' % self.utXmlEncode(self.title))
        ra('<link>%s</link>' % s.absolute_url())
        ra('<description><![CDATA[%s]]></description>' % self.utToUtf8(self.description))
        ra('<dc:description><![CDATA[%s]]></dc:description>' % self.utToUtf8(self.description))
        ra('<dc:identifier>%s</dc:identifier>' % s.absolute_url())
        ra('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.utGetTodayDate()))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(s.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(s.getLocalProperty('creator', lang)))
        ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(s.getLocalProperty('site_title', lang)))
        ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(s.getLocalProperty('site_subtitle', lang)))
        ra('<dc:language>%s</dc:language>' % self.utXmlEncode(lang))
        ra('<dc:rights>%s</dc:rights>' % self.utXmlEncode(s.getLocalProperty('rights', lang)))
        ra('<dc:type>%s</dc:type>' % self.utXmlEncode(self.type))
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(s.getLocalProperty('publisher', lang)))
        ra('<items>')
        ra('<rdf:Seq>')
        for i in l_items:
            ra('<rdf:li resource="%s"/>' % i.absolute_url())
        ra('</rdf:Seq>')
        ra('</items>')
        ra('</channel>')
        if self.hasImage():
            ra('<image>')
            ra('<title>%s</title>' % self.utXmlEncode(self.title))
            ra('<url>%s</url>' % self.getImagePath())
            ra('<link>%s</link>' % s.absolute_url())
            ra('<description><![CDATA[%s]]></description>' % self.utToUtf8(self.description))
            ra('</image>')
        for i in l_items:
            ra(i.syndicateThis(lang))
        ra("</rdf:RDF>")
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return ''.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/scriptchannel_properties', globals())

InitializeClass(ScriptChannel)
