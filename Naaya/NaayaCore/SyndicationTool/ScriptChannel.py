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
import new
from webdav.common import rfc1123_date

#Zope imports
from Acquisition import aq_parent
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PythonScripts.PythonScript import PythonScript
from Products.PythonScripts.PythonScript import PythonScriptTracebackSupplement
from Products.PythonScripts.PythonScript import _marker
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.StandardCacheManagers.RAMCacheManager import manage_addRAMCacheManager

#Product imports
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

    # Set cache manager
    if not 'cache_syndication' in self.objectIds():
        manage_addRAMCacheManager(self, 'cache_syndication')
    ob.ZCacheable_setManagerId('cache_syndication')

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class ScriptChannel(PythonScript, utils):
    """ """

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

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        PythonScript.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.delete_portlet_for_object(item)

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

    def _exec(self, bound_names, args, kw):
        """Call a Python Script no-cache. Will cache in __call__
        """
        ft = self._v_ft
        if ft is None:
            __traceback_supplement__ = (
                PythonScriptTracebackSupplement, self)
            raise RuntimeError, '%s %s has errors.' % (self.meta_type, self.id)

        fcode, g, fadefs = ft
        g = g.copy()
        if bound_names is not None:
            g.update(bound_names)
        g['__traceback_supplement__'] = (
            PythonScriptTracebackSupplement, self, -1)
        g['__file__'] = getattr(self, '_filepath', None) or self.get_filepath()
        f = new.function(fcode, g, None, fadefs)

        result = f(*args, **kw)
        return result
    
    def get_objects_for_rdf(self):
        #return the objects to be syndicated
        return self._exec({'context': self, 'container': self}, {}, {})
    
    # XXX Move to SyndicationTool
    def syndicateRdf(self, docs=[]):
        s = self.getSite()
        lang = self.language
        if lang == 'auto':
            lang = self.gl_get_selected_language()
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
        for doc in docs:
            ra('<rdf:li resource="%s"/>' % doc.absolute_url())
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
        for doc in docs:
            ra(doc.syndicateThis(lang))
        ra("</rdf:RDF>")
        return '\n'.join(r)
    
    def index_html(self, REQUEST, RESPONSE):
        """ Look in cache:
              - if item exists in cache:
                  if If-Modified-Sience in REQUEST headers:
                    set status 304, Not Modified
                    return ''
                  return cached value
              - else
                  compute result cache and return it.
        """
        RESPONSE.setHeader('Cache-Control', 'public,max-age=3600')
        RESPONSE.setHeader('Content-Type', 'text/xml')
        
        kwargs = REQUEST.form
        
        # Get page from cache if exists
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = kwargs.copy()
            asgns = self.getBindingAssignments()
            name_context = asgns.getAssignedName('name_context', None)
            if name_context:
                keyset[name_context] = aq_parent(self).getPhysicalPath()
            name_subpath = asgns.getAssignedName('name_subpath', None)
            if name_subpath:
                keyset[name_subpath] = self._getTraverseSubpath()
            # Note: perhaps we should cache based on name_ns also.
            keyset['*'] = ()
            result = self.ZCacheable_get(keywords=keyset, default=_marker)
            if result is not _marker:
                last_mod_req = REQUEST.get_header('If-Modified-Since', None)
                if not last_mod_req:
                    # Return from server cache
                    REQUEST.RESPONSE.setHeader('Last-Modified', rfc1123_date())
                    return result
                # Return from client cache
                RESPONSE.setStatus(304)
                return ''
        # Compute feed
        docs = self.get_objects_for_rdf()
        feed = kwargs.get('feed', '')
        if feed == 'atom':
            result = self.syndicateAtom(self, docs, self.language)
        else:
            result = self.syndicateRdf(docs)
        
        # Update cache
        if keyset is not None:
            self.ZCacheable_set(result, keywords=keyset)
        REQUEST.RESPONSE.setHeader('Last-Modified', rfc1123_date())
        return result

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/scriptchannel_properties', globals())

InitializeClass(ScriptChannel)
