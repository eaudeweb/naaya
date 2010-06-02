# -*- coding: iso-8859-15 -*-
#################################################################################
#										#
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,		#
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez    		#
# Christian Martel								#
#										#
# This program is free software; you can redistribute it and/or			#
# modify it under the terms of the GNU General Public License			#
# as published by the Free Software Foundation; either version 2		#
# of the License, or (at your option) any later version.			#
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software      		#
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#										#
#################################################################################

__doc__ = """ Zope OAI Site Record """


import urllib
import string
import DateTime
import xml.dom.minidom
import App
import Globals
from Globals import HTMLFile
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from types import StringType, UnicodeType
from pyOAIMH.OAIRecord import OAIRecord

from utils import processId


# there is no interface to add these. addition
#   is done directly from the code
#
def manage_addOAIRecord(self, id=None, metadata_format=None, xml=None, dom=None):
    """ method for adding a new OAI object """
    # have to add metadata format to end of ID
    #   because we could have many records for
    #   one single object
    try:
        id = processId(id)
        OAIR = zOAIRecord(id, metadata_format=metadata_format, xml=xml, dom=dom)
    except:
        import traceback
        traceback.print_exc()
    self._setObject(id, OAIR)

    # get back OAI Record object
    OAIR = getattr(self, id)
    OAIR.initialize()
    OAIR.index_object()


class zOAIRecord(OAIRecord,App.Management.Navigation, SimpleItem, Implicit):
    """ """

    meta_type = 'Open Archive Record'
    default_document = 'index_html'
    default_catalog = 'OAI_Catalog'

    manage_options= (
        { 'label': 'Information', 'action': 'index_html'},
    )

    index_html = HTMLFile("dtml/manage_OAIRecordForm",globals())

    def __init__(self, id, metadata_format=None, xml=None, dom=None, timestr=""):
        """
        TODO: change so it accepts string or dom xml
        """
        self.id = id
        self.last_update = None
        try:
            OAIRecord.__init__(self, metadata_format=metadata_format,
                               xml=xml, dom=dom)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            OAIRecord.__init__.im_func(self, metadata_format=metadata_format,
                                       xml=xml, dom=dom)

    def getHeader(self):
        """ """
        return self._encode(self.header)

    def getMetadata(self):
        """ """
        return self._encode(self.metadata)

    def getStatus(self):
        """ """
        return self._encode(self.status)


    def initialize(self):
        """ """
        zOAIRecord.inheritedAttribute("initialize")(self)
        self.last_update = DateTime.DateTime()

    def update_Record(self, xml=None):
        """
        """
        # TODO: add stuff for update Record
        # this check is so we can pass in xml=None to update record
        #  all records which haven't been updated are
        #  assume to be deleted
        if xml != None:
            zOAIRecord.inheritedAttribute('update_Record')(self, xml=xml)
        self.last_update = DateTime.DateTime()
        self.reindex_object()

    def mark_recordDeleted(self):
        """
        """
        zOAIRecord.inheritedAttribute("mark_recordDeleted")(self)
        self.last_update = DateTime.DateTime()
        self.reindex_object()

    def get_myContainer(self):
        """ get my parent container """
        return self.aq_parent

    def index_object(self):
        """
        """
        getattr(self, self.default_catalog).catalog_object(self, urllib.unquote('/' + self.absolute_url(1) ))

    def unindex_object(self):
        """
        """
        getattr(self, self.default_catalog).uncatalog_object(urllib.unquote('/' + self.absolute_url(1) ))

    def reindex_object(self):
        """
        """
        self.unindex_object()
        self.index_object()

    def manage_beforeDelete(self, item, container):
        """ do stuff before being deleted """
        # remove object from catalog
        self.unindex_object()
        zOAIRecord.inheritedAttribute("manage_beforeDelete")(self,item,container)

    # ###########
    # OAI Catalog Metadata Methods
    # prefix of 'dc_' is necessary for advSearchXML

    def do_HeaderListInterface(self,info_tags=[]):
        """
        tag - metadata tag group-name in xml eg, 'dc'
        info_tags - name(s) of tags to collect data from
        """
        return self.get_HeaderList( tags=info_tags )

    def do_MetadataListInterface(self, ns, ns_tag, info_tags=[]):
        """
        ns = namespace in oai server
        ns_tag - metadata tag group-name in xml eg, 'dc'
        info_tags - name(s) of tags to collect data from
        """
        ns_dict = self.get_myContainer().get_myContainer().get_namespaceInfoByPrefix(ns)
        return self.get_MetadataList( ns_name=ns_tag, tags=info_tags,
                                      ns_qualifiers=[None, ns_dict['namespace']])

    def dc_title(self):
        """ """
        list = self.do_MetadataListInterface('oai_dc', 'dc', ['title'])
        return string.join(map(self._encode,list))

    def dc_creator(self):
        """ """
        paths = [['metadata','oai_dc','creator'],['metadata','oaidc:dc','creator'], ['metadata','dc','creator'],['metadata','oai_dc:dc','dc:creator']]
        dom = self.get_DOM('metadata')
        creator_str = ""
        if not dom: return creator_str
        for path in paths:
            for creator_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                creator_str = creator_str + self.getDOMElementText(dom_node=creator_dom, encode=self.default_encoding)
            creator_str += ' '

        return creator_str.strip()
       ## list = self.do_MetadataListInterface('oai_dc', 'dc', ['creator'])
       ## return string.join(map(self._encode,list))

    def dc_author(self):
        """ """
        paths = [['metadata','oai_dc','author'],['metadata','oaidc:dc','author'], ['metadata','dc','author'],['metadata','oai_dc:dc','dc:author']]
        dom = self.get_DOM('metadata')
        author_str = ""
        if not dom: return author_str
        for path in paths:
            for author_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                author_str = author_str + self.getDOMElementText(dom_node=author_dom, encode=self.default_encoding)
            author_str += ' '
        return author_str.strip()

    def dc_type(self):
        """ """
        paths = [['metadata','oai_dc','type'],['metadata','oaidc:dc','type'], ['metadata','dc','type'],['metadata','oai_dc:dc','dc:type']]
        dom = self.get_DOM('metadata')
        type_str = ""
        if not dom: return type_str
        for path in paths:
            for type_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                type_str = type_str + self.getDOMElementText(dom_node=type_dom, encode=self.default_encoding)
            type_str += ' '
        return type_str.strip()

    def dc_subject(self):
        """ """
        list = self.do_MetadataListInterface('oai_dc', 'dc', ['subject'])
        return string.join(map(self._encode,list))

    def dc_description(self):
        """ """
        paths = [['metadata','oai_dc','description'],['metadata','oaidc:dc','description'], ['metadata','dc','description'],['metadata','oai_dc:dc','dc:description']]
        dom = self.get_DOM('metadata')
        description_str = ""
        if not dom: return description_str
        for path in paths:
            for description_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                description_str = description_str + self.getDOMElementText(dom_node=description_dom , encode=self.default_encoding)
            description_str += ' '
        return description_str.strip()
##        list = self.do_MetadataListInterface('oai_dc', 'dc', ['description'])
##        return string.join(map(self._encode,list))

    def dc_publisher(self):
        """ """
        return []

    def dc_contributor(self):
        """ """
        return []

    def dc_date(self):
        """ """
        list = self.do_MetadataListInterface('oai_dc', 'dc', ['date'])
        return string.join(map(self._encode,list))

    def dc_format(self):
        """ """
        return []

    def dc_identifier(self):
        """ """
        paths = [['metadata','oai_dc','identifier'],['metadata','oaidc:dc','identifier'], ['metadata','dc','identifier'],['metadata','oai_dc:dc','dc:identifier']]
        dom = self.get_DOM('metadata')
        identifier_str = ""
        lIdentifier = []
        if not dom: return identifier_str
        for path in paths:
            for identifier_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                lIdentifier.append(self.getDOMElementText(dom_node=identifier_dom, encode=self.default_encoding))
                break
            if lIdentifier !=[]:
                for identif in lIdentifier:
                    if string.find(identif,'http')!=-1:
                        return identif
                return lIdentifier[0]

        return identifier_str.strip()
##        id = self.do_MetadataListInterface('oai_dc', 'dc', ['identifier'] )
##        return string.join(id)

    def dc_source(self):
        """ """
        return []

    def dc_language(self):
        """ """
        return []

    def dc_relation(self):
        """ """
        return []

    def dc_coverage(self):
        """ """
        return []

    def dc_rights(self):
        """ """
        return []

    # ###########
    # OAI Catalog methods

    def _encode(self, item):
        """ """
        if isinstance(item, UnicodeType):
            item = item.encode(self.default_encoding)
        return item

    def OAI_Fulltext(self):
        """
        is a TextIndex in catalog
        return text string
        """
        paths = [ ['metadata','oai_dc','title'],
                  ['metadata','oai_dc','subject'],
                  ['metadata','oai_dc','description'],
                  ['metadata','dc','dc:title'],
                  ['metadata','dc','dc:subject'],
                  ['metadata','dc','dc"description'],
                  ['metadata','oai_dc:dc','dc:title'],
                  ['metadata','oai_dc:dc','dc:subject'],
                  ['metadata','oai_dc:dc','dc:description'],
                  ['metadata','dc','dc:title'],
                  ['metadata','dc','dc:subject'],
                  ['metadata','dc','dc:description'],
                  ['metadata','oaidc:dc','title'],
                  ['metadata','oaidc:dc','subject'],
                  ['metadata','oaidc:dc','description']
                ]
        dom = self.get_DOM('metadata')
        text_str = ""
        if not dom: return text_str
        for path in paths:
            for text_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                text_str = text_str + self.getDOMElementText(dom_node=text_dom, encode=self.default_encoding)
            text_str += ' '
        return text_str

    def OAI_Title(self):
        """
        is a TextIndex in catalog
        return text string
        """
        paths = [['metadata','oai_dc','title'],['metadata','oaidc:dc','title'], ['metadata','dc','title'],['metadata','oai_dc:dc','dc:title']]
        dom = self.get_DOM('metadata')
        title_str = ""
        if not dom: return title_str
        for path in paths:
            for title_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
                title_str = title_str + self.getDOMElementText(dom_node=title_dom, encode=self.default_encoding)
            title_str += ' '
        return title_str


    def OAI_MetadataFormat(self):
        """ """
        return self.metadata_format

    def OAI_Date(self):
        """
        is a DateIndex
        return date timestring date
        """
        path = ['header','datestamp']
        dom = self.get_DOM('header')
        date_str = ''
        if not dom: return date_str
        for date_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
            date_str = date_str + self.getDOMElementText(dom_node=date_dom, encode=self.default_encoding)

        date = DateTime.DateTime(date_str)
        return date.aCommon()

    def OAI_Set(self):
        """ """
        return "set"

    def OAI_Identifier(self):
        """ """
        path = ['header','identifier']
        dom = self.get_DOM('header')
        id = ''
        if not dom: return id
        for id_dom in self.findDOMElements( dom_list=[dom], tag_path=path ):
            id = id + self.getDOMElementText(dom_node=id_dom, encode=self.default_encoding)
        return id

# helper methods for other classes
#

def create_ObjectMetadata(object, obj_data, ns_dict=None, type='xml', def_enc='UTF-8'):
    """
    create the XML structure
    obj_data is a dict containing info from object.
    type = 'xml' or 'dom'
    """
    # start XML record
    xmldoc = xml.dom.minidom.Document()
    xmldoc.createProcessingInstruction('xml', 'version="1.0" encoding="%s"' % def_enc )

    # create <record> node
    record = xmldoc.createElement("record")
    xmldoc.appendChild(record)

    # create <header> node
    # TODO: change datestamps to proper encoding
    header = xmldoc.createElement("header")
    record.appendChild(header)

    h_tags = obj_data['header_tags']
    for tagname in h_tags.keys():
        data = h_tags[tagname]
        tag = xmldoc.createElement(tagname)
        tag.appendChild(xmldoc.createTextNode(str(data)))
        header.appendChild(tag)

    # create <metadata> node
    # list format - tag name, field data (object attr)
    #
    # title, creator, subject, description, publisher, contributor
    # date, type, format, identifier, source, language, relation
    # coverage, rights
    metadata = xmldoc.createElement("metadata")
    record.appendChild(metadata)
    if ns_dict != None:
        dc = xmldoc.createElementNS(ns_dict['namespace'], "oai_dc:dc")
        #dc.setAttributeNS(ns_dict['namespace'],"xmlns", ns_dict['namespace'])
        dc.setAttributeNS(ns_dict['namespace'],"xmlns:oai_dc", ns_dict['namespace'])
        dc.setAttributeNS(ns_dict['namespace'],"xmlns:dc", "http://purl.org/dc/elements/1.1/")
    metadata.appendChild(dc)

##    # add namespace attributes if applicable
##    #
##    if ns_dict != None:
##        dc.setAttributeNS(ns_dict['namespace'],"xmlns", ns_dict['namespace'])
##        dc.setAttributeNS(ns_dict['namespace'],"xmlns:oai_dc", ns_dict['namespace'])
    m_tags = obj_data['metadata_tags']
    for tagname in m_tags.keys():
        data = m_tags[tagname]
        if data:
            if getType(data) == getType((1,)):
              data = string.join(data)
            # change accents to character references
            the_str = ""
            for char in data:
                o = ord(char)
                if o < 32 or o > 126:
                    the_str += "&#%s;" % o
                else:
                    the_str += char

            data = the_str
            if not isinstance(data, UnicodeType):
                data = unicode(data, def_enc)
            tag = xmldoc.createElement(tagname)
            tag.appendChild(xmldoc.createTextNode(data))
            dc.appendChild(tag)
    if type=='xml':
        return xmldoc.toxml(def_enc)
    elif type=='dom':
        return xmldoc
    else:
        raise error, "create_ObjectMetadata: value not known"

def getType(param):
    """ """
    return type(param)
