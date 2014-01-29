"""
This module contains the base class of Naaya architecture.

"""

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass
from Acquisition import aq_base
from zope.event import notify

from naaya.content.base.events import (NyContentObjectApproveEvent,
                                       NyContentObjectUnapproveEvent)

from naaya.core.utils import replace_illegal_xml
from NyCheckControl import NyCheckControl
from NyDublinCore import NyDublinCore
from Products.NaayaCore.managers.utils import get_nsmap

from lxml import etree
from lxml.builder import ElementMaker

class NyBase(NyDublinCore):
    """
    The base class of Naaya architecture. It implements basic functionality
    common to all classes.
    """

    def __init__(self):
        """
        Initialize variables.

        `submitted` - flag that signals if the object has been
        submited or not; it applies for object such as Story and Document.

        """

        self.submitted = 0

    security = ClassSecurityInfo()

    #test for subclasses
    security.declareProtected(view, 'isVersionable')
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
    def approveThis(self, approved=1, approved_by=None,
                    _send_notifications=True):
        """
        Set the state of the current object.
        @param approved: the state flag
        @type approved: integer - 0 or 1
        """

        #If approved attribute is not changed - do nothing
        if hasattr(aq_base(self), 'approved') and self.approved == approved:
            return

        if approved_by is None:
            approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()

        self.approved = approved
        self.approved_by = approved_by
        self._p_changed = 1

        #Trigger approval events
        if self.approved:
            notify(NyContentObjectApproveEvent(self, approved_by,
                                    _send_notifications=_send_notifications))
        else:
            notify(NyContentObjectUnapproveEvent(self, approved_by,
                                    _send_notifications=_send_notifications))

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
        """Builds the object keywords from common multilingual properties"""
        return u' '.join([
            self.getLocalProperty('title', lang),
            self.getLocalProperty('description', lang),
            self.getLocalProperty('coverage', lang),
            self.getLocalProperty('keywords', lang)
        ])

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

    def _tags(self, lang):
        """
        For each portal language an index I{tags}_I{lang} is created.
        Process the keywords for the specific catalog index.

        B{This method can be overwritten by some types of objects if additonal
        properties values must be considered as keywords.}
        @param lang: the index language
        @type lang: string
        """

        return filter(None, self.getLocalProperty('keywords', lang).split(','))

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

    security.declarePrivate('non_empty_title')
    def non_empty_title(self, lang):
        title = self.getLocalProperty('title', lang)
        if title:
            return title
        d_title = self.getLocalProperty('title', self.gl_get_default_language())
        if d_title:
            return d_title
        for lang in self.gl_get_languages():
            lang_title = self.getLocalProperty('title', lang)
            if lang_title:
                return lang_title
        return self.title_or_id()

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
        ra('<title>%s</title>' % self.utXmlEncode(self.non_empty_title(lang)))
        ra('<description><![CDATA[%s]]></description>' % self.utToUtf8(self.getLocalProperty('description', lang)))
        ra('<dc:title>%s</dc:title>' % self.utXmlEncode(self.non_empty_title(lang)))
        ra('<dc:identifier>%s</dc:identifier>' % self.identifier())
        ra('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.releasedate))
        ra('<dc:description><![CDATA[%s]]></dc:description>' % self.utToUtf8(self.getLocalProperty('description', lang)))
        ra('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(self.contributor))
        ra('<dc:language>%s</dc:language>' % self.utXmlEncode(lang))
        for k in self.getLocalProperty('coverage', lang).split(','):
            ra('<dc:coverage>%s</dc:coverage>' % self.utXmlEncode(k.strip()))
        for k in self.getLocalProperty('keywords', lang).split(','):
            ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(k.strip()))
        ra('<dc:rights>%s</dc:rights>' % self.utXmlEncode(self.rights))
        return ''.join(r)

    #Syndication RDF
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
        syndication_tool = self.getSyndicationTool()
        namespaces = syndication_tool.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        rdf_namespace = nsmap['rdf']
        dc_namespace = nsmap['dc']
        Rdf = ElementMaker(namespace=rdf_namespace, nsmap=nsmap)
        Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
        E = ElementMaker(None, nsmap=nsmap)
        xml = Rdf.RDF(
                E.item(
                    {'{%s}about'%rdf_namespace : self.absolute_url()},
                    E.link(self.absolute_url()),
                    E.title(self.non_empty_title(lang)),
                    E.description(self.getLocalProperty('description', lang)),
                    Dc.title(self.non_empty_title(lang)),
                    Dc.identifier(self.identifier()),
                    Dc.date(self.utShowFullDateTimeHTML(self.releasedate)),
                    Dc.description(self.getLocalProperty('description', lang)),
                    Dc.contributor(self.contributor),
                    Dc.language(lang)
                )
            )
        item = xml[0]
        for k in self.getLocalProperty('coverage', lang).split(','):
            item.append(Dc.coverage(k.strip()))
        for k in self.getLocalProperty('keywords', lang).split(','):
            item.append(Dc.subject(k.strip()))
        item.append(Dc.rights(self.getLocalProperty('rights', lang)))
        the_rest = (
                Dc.publisher(l_site.getLocalProperty('publisher', lang)),
                Dc.creator(l_site.getLocalProperty('creator', lang)),
                Dc.type(self.type()),
                Dc.format(self.format()),
                Dc.source(l_site.getLocalProperty('publisher', lang)),
               )
        item.extend(the_rest)
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

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
        """Opens the object tag for the current object. Common non multilingual
        object properties are added as tag attributes.

        `param` - this attribute tells the import engine what to do with
        the current object:

          0. try to create the object even if the object exists
          1. try to create the object, but if the object exists the old
             object must be deleted first
          2. the object already exists (do nothing)
          3. try to delete the object and all its content

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
        ra(self.export_comments())
        return ''.join(r)

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        """
        B{This method can be overwritten by some types of objects in order to
        export specific object data as tags.}
        """

        return ''

    security.declarePrivate('ny_ldap_group_roles')
    @property # this is used in brains by Catalog
    def ny_ldap_group_roles(self):
        return getattr(self, '__ny_ldap_group_roles__', {})

InitializeClass(NyBase)

def rss_item_for_object(obj,lang):
    syndication_tool = obj.getSyndicationTool()
    namespaces = syndication_tool.getNamespaceItemsList()
    nsmap = get_nsmap(namespaces)
    dc_namespace = nsmap['dc']
    Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
    rdf_namespace = nsmap['rdf']
    E = ElementMaker(None, nsmap=nsmap)
    xml = E.item(
        {'{%s}about'%rdf_namespace : obj.absolute_url()},
        E.link(replace_illegal_xml(obj.absolute_url())),
        E.title(replace_illegal_xml(obj.non_empty_title(lang))),
        E.description(replace_illegal_xml(obj.getLocalProperty('description', lang))),
        Dc.title(replace_illegal_xml(obj.non_empty_title(lang))),
        Dc.identifier(replace_illegal_xml(obj.identifier())),
        Dc.date(obj.utShowFullDateTimeHTML(obj.releasedate)),
        Dc.description(replace_illegal_xml(obj.getLocalProperty('description', lang))),
        Dc.contributor(replace_illegal_xml(obj.contributor)),
        Dc.language(lang)
        )
    for k in obj.getLocalProperty('coverage', lang).split(','):
        xml.append(Dc.coverage(replace_illegal_xml(k.strip())))
    for k in obj.getLocalProperty('keywords', lang).split(','):
        xml.append(Dc.subject(replace_illegal_xml(k.strip())))
    xml.append(Dc.rights(replace_illegal_xml(obj.rights)))
    return xml

rdf_ns_map = {
    'ev' : 'http://purl.org/rss/1.0/modules/event/',
    'dc' : 'http://purl.org/dc/elements/1.1/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'a' : 'http://purl.org/rss/1.0/'
}
