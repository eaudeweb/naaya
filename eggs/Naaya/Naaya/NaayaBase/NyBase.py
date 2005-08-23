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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from AccessControl.Permissions import view_management_screens

#Product imports
from constants import *

class NyBase:
    """ """

    security = ClassSecurityInfo()

    security.declarePrivate('getObjectOwner')
    def getObjectOwner(self):
        ownerid = None
        ownerinfo = self.owner_info()
        if hasattr(ownerinfo, "has_key") and ownerinfo.has_key('id'):
            ownerid = ownerinfo['id']
        return ownerid

    security.declarePrivate('getObjectOwnerFullName')
    def getObjectOwnerFullName(self):
        ownerid = self.getObjectOwner()
        user_obj = self.getAuthenticationTool().getUser(ownerid)
        if user_obj is not None:
            owner_full_name = user_obj.firstname + ' '+ user_obj.lastname
            return owner_full_name
        else:
            return ownerid

    security.declarePrivate('approveThis')
    def approveThis(self, approved=1):
        self.approved = approved
        self._p_changed = 1

    security.declareProtected(view_management_screens, 'setReleaseDate')
    def setReleaseDate(self, releasedate):
        """ """
        self.releasedate = self.utGetDate(releasedate)
        self._p_changed = 1

    def _objectkeywords(self, lang):
        l_values = [self.getLocalProperty('title', lang), self.getLocalProperty('description', lang), self.getLocalProperty('keywords', lang)]
        #for l_dp in self.getDynamicPropertiesTool().getDynamicSearchableProperties(self.meta_type):
        #    l_values.append(self.getPropertyValue(l_dp.id, lang))
        return u' '.join([x for x in l_values])

    def objectkeywords(self, lang):
        return self._objectkeywords(lang)

    def istranslated(self, lang):
        #an object is considered to be translated into a language if
        #the value of the 'title' property in that language is not an empty string
        return self.getLocalProperty('title', lang) != ''

    #security
    def checkPermission(self, p_permission):
        return getSecurityManager().checkPermission(p_permission, self)

    def checkPermissionAdministrate(self):
        return self.checkPermission(PERMISSION_ADMINISTRATE)

    def checkPermissionPublishObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionEditObjects(self):
        return self.checkPermission(PERMISSION_EDIT_OBJECTS)

    def checkPermissionCopyObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionCutObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionPasteObjects(self):
        return self.checkPermission(PERMISSION_PUBLISH_OBJECTS)

    def checkPermissionDeleteObjects(self):
        return self.checkPermission(PERMISSION_DELETE_OBJECTS)

    def checkPermissionValidateObjects(self):
        return self.checkPermission(PERMISSION_VALIDATE_OBJECTS)

    def checkPermissionTranslatePages(self):
        return self.checkPermission(PERMISSION_TRANSLATE_PAGES)

    def checkPermissionEditObject(self):
        return self.checkPermissionEditObjects() and (self.checkPermissionPublishObjects() or (self.getObjectOwner() == self.REQUEST.AUTHENTICATED_USER.getUserName()))

    def checkPermissionDeleteObject(self):
        return self.checkPermissionDeleteObjects() and self.checkPermissionPublishObjects()

    #Syndication RDF
    security.declarePrivate('syndicateThisHeader')
    def syndicateThisHeader(self):
        return '<item rdf:about="%s">' % self.absolute_url(0)

    security.declarePrivate('syndicateThisFooter')
    def syndicateThisFooter(self):
        return '</item>'

    security.declarePrivate('syndicateThisCommon')
    def syndicateThisCommon(self):
        l_rdf = []
        l_rdf.append('<link>%s</link>' % self.absolute_url())
        l_rdf.append('<dc:title>%s</dc:title>' % self.utXmlEncode(self.title_or_id()))
        l_rdf.append('<dc:identifier>%s</dc:identifier>' % self.absolute_url())
        l_rdf.append('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.releasedate))
        l_rdf.append('<dc:description>%s</dc:description>' % self.utXmlEncode(self.description))
        l_rdf.append('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(self.contributor))
        l_rdf.append('<dc:coverage>%s</dc:coverage>' % self.utXmlEncode(self.coverage))
        l_rdf.append('<dc:language>%s</dc:language>' % self.utXmlEncode(self.gl_get_selected_language()))
        for l_k in self.keywords.split(' '):
            l_rdf.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(l_k))
        l_rdf.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(self.creator))
        l_rdf.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(self.publisher))
        l_rdf.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(self.rights))
        return ''.join(l_rdf)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self):
        l_rdf = []
        l_rdf.append(self.syndicateThisHeader())
        l_rdf.append(self.syndicateThisCommon())
        l_rdf.append('<dc:type>Text</dc:type>')
        l_rdf.append('<dc:format>text</dc:format>')
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(self.publisher))
        l_rdf.append(self.syndicateThisFooter())
        return ''.join(l_rdf)

    #Handlers for export in xml format
    security.declarePrivate('export_this')
    def export_this(self):
        r = []
        r.append(self.export_this_tag())
        r.append(self.export_this_body())
        r.append('</ob>')
        return ''.join(r)

    security.declarePrivate('export_this_tag')
    def export_this_tag(self):
        return '<ob meta_type="%s" id="%s" sortorder="%s" contributor="%s" approved="%s" approved_by="%s" releasedate="%s" %s>' % \
            (self.utXmlEncode(self.meta_type),
             self.utXmlEncode(self.id),
             self.utXmlEncode(self.sortorder),
             self.utXmlEncode(self.contributor),
             self.utXmlEncode(self.approved),
             self.utXmlEncode(self.approved_by),
             self.utXmlEncode(self.releasedate),
             self.export_this_tag_custom())

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return ''

    security.declarePrivate('export_this_body')
    def export_this_body(self):
        r = []
        for l in self.gl_get_languages():
            v = self.getLocalProperty('title', l)
            if isinstance(v, unicode): v = v.encode('utf-8')
            r.append('<title lang="%s" content="%s"/>' % (l, self.utXmlEncode(v)))
            v = self.getLocalProperty('description', l)
            if isinstance(v, unicode): v = v.encode('utf-8')
            r.append('<description lang="%s" content="%s"/>' % (l, self.utXmlEncode(v)))
            v = self.getLocalProperty('coverage', l)
            if isinstance(v, unicode): v = v.encode('utf-8')
            r.append('<coverage lang="%s" content="%s"/>' % (l, self.utXmlEncode(v)))
            v = self.getLocalProperty('keywords', l)
            if isinstance(v, unicode): v = v.encode('utf-8')
            r.append('<keywords lang="%s" content="%s"/>' % (l, self.utXmlEncode(v)))
        r.append(self.export_this_body_custom())
        return ''.join(r)

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        return ''

InitializeClass(NyBase)
