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
# The Original Code is Naaya version 1.0
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

"""
This module contains the base class of Naaya architecture.
"""

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass

#Product imports
from constants import *
from NyCheckControl import NyCheckControl

class NyBase:
    """
    The base class of Naaya architecture. It implements basic functionality
    common to all classes.
    """

    def __init__(self):
        """
        Initialize variables:

        B{submitted} - flag that signals if the object has been
        submited or not; it applies for object such as Story and Document.

        """
        self.submitted = 0

    security = ClassSecurityInfo()

    #test for subclasses
    security.declarePrivate('isVersionable')
    def isVersionable(self):
        """
        Test if the current object is instance of the B{NyCheckControl} class.
        """
        return isinstance(self, NyCheckControl)

    security.declareProtected(view_management_screens, 'setContributor')
    def setContributor(self, contributor):
        """
        Set the contributor for the current object.
        @param contributor: the contributor
        @type contributor: string
        """
        self.contributor = contributor
        self._p_changed = 1

    security.declarePrivate('approveThis')
    def approveThis(self, approved=1, approved_by=None):
        """
        Set the state of the current object.
        @param approved: the state flag
        @type approved: integer - 0 or 1
        """
        if approved_by is None: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.approved = approved
        self.approved_by = approved_by
        self._p_changed = 1
        #call hooks for (un)approve operations
        if self.approved:
            self.hook_after_approve(self)
        else:
            self.hook_after_unapprove(self)

    security.declarePrivate('setReleaseDate')
    def setReleaseDate(self, releasedate):
        """
        Set the release date of the current object.
        @param releasedate: the date
        @type releasedate: DateTime
        """
        self.releasedate = self.utGetDate(releasedate)
        self._p_changed = 1

    security.declarePrivate('submitThis')
    def submitThis(self):
        """
        Set the submit flag for the current object.

        B{0} - the objects is not yet fully created

        B{1} - the object has been created
        """
        self.submitted = 1
        self._p_changed = 1

    def _objectkeywords(self, lang):
        """
        Builds the object keywords from common multilingual properties.
        @param lang: the index language
        @type lang: string
        """
        v = [self.getLocalProperty('title', lang), self.getLocalProperty('description', lang),
             self.getLocalProperty('coverage', lang), self.getLocalProperty('keywords', lang)]
        #for l_dp in self.getDynamicPropertiesTool().getDynamicSearchableProperties(self.meta_type):
        #    v.append(self.getPropertyValue(l_dp.id, lang))
        return u' '.join(v)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        """
        For each portal language an index I{objectkeywords}_I{lang} is created.
        Process the keywords for the specific catalog index.

        B{This method can be overwritten by some types of objects if additonal
        properties values must be considered as keywords.}
        @param lang: the index language
        @type lang: string
        """
        return self._objectkeywords(lang)

    security.declarePublic('istranslated')
    def istranslated(self, lang):
        """
        An object is considered to be translated into a language if
        the value of the I{title} property in that language is not an empty string.
        @param lang: the index language
        @type lang: string
        """
        return len(self.getLocalProperty('title', lang)) > 0

    #Syndication RDF
    security.declarePrivate('syndicateThisHeader')
    def syndicateThisHeader(self):
        """
        Opens the item RDF tag for the current object.
        """
        return '<item rdf:about="%s">' % self.absolute_url()

    security.declarePrivate('syndicateThisFooter')
    def syndicateThisFooter(self):
        """
        Closes the item RDF tag for the current object.
        """
        return '</item>'

    security.declarePrivate('syndicateThisCommon')
    def syndicateThisCommon(self, lang):
        """
        Common RDF content (tags) for all types of objects.
        @param lang: content language
        @type lang: string
        """
        r = []
        ra = r.append
        ra('<link>%s</link>' % self.absolute_url())
        ra('<title>%s</title>' % self.utXmlEncode(self.getLocalProperty('title', lang)))
        ra('<description><![CDATA[%s]]></description>' % self.utToUtf8(self.getLocalProperty('description', lang)))
        ra('<dc:title>%s</dc:title>' % self.utXmlEncode(self.getLocalProperty('title', lang)))
        ra('<dc:identifier>%s</dc:identifier>' % self.identifier())
        ra('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.releasedate))
        ra('<dc:description><![CDATA[%s]]></dc:description>' % self.utToUtf8(self.getLocalProperty('description', lang)))
        ra('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(self.contributor))
        ra('<dc:language>%s</dc:language>' % self.utXmlEncode(lang))
        for k in self.getLocalProperty('coverage', lang).split(','):
            ra('<dc:coverage>%s</dc:coverage>' % self.utXmlEncode(k.strip()))
        for k in self.getLocalProperty('keywords', lang).split(','):
            ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(k.strip()))
        ra('<dc:rights>%s</dc:rights>' % self.utXmlEncode(self.getLocalProperty('rights', lang)))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        """
        Generates RDF item tag for an object.

        B{This method can be overwritten by some types of objects in order to
        add specific tags.}
        @param lang: content language
        @type lang: string
        """
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:type>%s</dc:type>' % self.type())
        ra('<dc:format>%s</dc:format>' % self.format())
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #Handlers for export in xml format
    security.declarePublic('export_this')
    def export_this(self):
        """
        Exports an object into Naaya XML format.

        B{This method can be overwritten by some types of objects in order to
        export specific data.}
        """
        r = []
        ra = r.append
        ra(self.export_this_tag())
        ra(self.export_this_body())
        ra('</ob>')
        return ''.join(r)

    security.declarePrivate('export_this_tag')
    def export_this_tag(self):
        """
        Opens the object tag for the current object. Common non multilingual
        object properties are added as tag attributes.

        B{param} - this attribute tells the import engine what to do with
        the current object:
            - B{0} - try to create the object even if the object exists
            - B{1} - try to create the object, but if the object exists the old
              object must be deleted first
            - B{2} - the object already exists (do nothing)
            - B{3} - try to delete the object and implicit all its content
        """
        return '<ob meta_type="%s" param="0" id="%s" sortorder="%s" contributor="%s" \
            approved="%s" approved_by="%s" releasedate="%s" discussion="%s" %s>' % \
            (self.utXmlEncode(self.meta_type),
             self.utXmlEncode(self.getId()),
             self.utXmlEncode(self.sortorder),
             self.utXmlEncode(self.contributor),
             self.utXmlEncode(self.approved),
             self.utXmlEncode(self.approved_by),
             self.utXmlEncode(self.releasedate),
             self.utXmlEncode(self.discussion),
             self.export_this_tag_custom())

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        """
        B{This method can be overwritten by some types of objects in order to
        export specific object data as attributes.}
        """
        return ''

    security.declarePrivate('export_this_body')
    def export_this_body(self):
        """
        Common multilingual object properties are added as tags.
        """
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<title lang="%s"><![CDATA[%s]]></title>' % (l, self.utToUtf8(self.getLocalProperty('title', l))))
            ra('<description lang="%s"><![CDATA[%s]]></description>' % (l, self.utToUtf8(self.getLocalProperty('description', l))))
            ra('<coverage lang="%s"><![CDATA[%s]]></coverage>' % (l, self.utToUtf8(self.getLocalProperty('coverage', l))))
            ra('<keywords lang="%s"><![CDATA[%s]]></keywords>' % (l, self.utToUtf8(self.getLocalProperty('keywords', l))))
        ra(self.export_this_body_custom())
        ra(self.export_this_comments())
        return ''.join(r)

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        """
        B{This method can be overwritten by some types of objects in order to
        export specific object data as tags.}
        """
        return ''

InitializeClass(NyBase)
