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

__doc__ = """ OAI Record object module  """


# non zope version
# works on <record> sections of OAI reponse

import xml.dom.minidom
import DateTime

from types import StringType, UnicodeType
from MyXMLLib import MyXMLLib

# this is for processing just the <record> portion of
#  an OAI response
#

class OAIRecord(MyXMLLib):
    
    default_encoding = 'UTF-8'

    def __init__(self, metadata_format=None, xml=None, dom=None):
        """ """
        self.header = ""     # store xml header section
        self.metadata = ""    # store xml metadata section
        self.about = ""       # store xml about section
        self.metadata_format = metadata_format
        self.status = 'available'      # "available" or "deleted"
        if xml == None and dom == None:
            raise "neither xml nor dom"
        elif xml != None and dom != None:
            raise "have both xml and dom"

        # if have xml, change to DOM
        if xml != None:
            dom = self.xml2dom(xml)
        self.handle_DOM(dom)

    def initialize(self):
        """ initialize any attributes """
        pass
       

    def update_Record(self, metadata_format='oai_dc', xml=None, dom=None):
        """
        - make a mix of __init__() without the initialize()
        - see if any changes need to be made before
          changing each section (eg, header, metadata, about)
        """
        self.status = 'available'
        self.handle_DOM(self.create_DOM(xmldata=xml))
        
    def mark_recordDeleted(self):
        """
        add deleted status in header
        """
        # add <header> attribute 'status'='deleted'
        header = None
        if self.header != "":
            dom = xml.dom.minidom.parseString(self.header)
            for h in dom.childNodes:
                if hasattr(h, 'tagName') and h.tagName == 'header':
                    header = h
                    break
                
        if header == None:
            raise "missing header in marg_record Deleted"

        header.setAttribute('status','deleted')

        h = self.get_HeaderXML(header)
##        if isinstance(h, UnicodeType):
##            h = h.encode(self.default_encoding)
##        if h = unicode(h, self.default_encoding)

        self.header = h
        self.metadata = ""
        self.about = ""
        self.status='deleted'

    def create_DOM(self, xmldata):
        """
        """
        dom = xml.dom.minidom.parseString(xmldata)
        return dom
    
    def get_DOM(self, select):
        """
        select = 'header', 'metadata', 'about'
        give XML section, get DOM of that XML
        """
        data = getattr(self, select, '')
        if data == '':
            return None
            print "ERROR in get_DOM: missing attr ", select
            raise error
        # data = unicode(data, self.default_encoding)
        if isinstance(data, UnicodeType):
            pass
        else:
            data =  '<?xml version="1.0" encoding="%s"?>' % self.default_encoding + data
            data = unicode(data, self.default_encoding)
        dom = xml.dom.minidom.parseString(data.encode(self.default_encoding))
        return dom


    def xml2dom(self, xmldata):
        """ """
        dom = xml.dom.minidom.parseString(xmldata)
        return dom
    
    def get_DOMText(self, nodelist):
        """
        return all text nodes
        can call with
        --> self.get_DOMText(item.childNodes)
        """
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc    
    
    def handle_DOM(self, dom):
        """
        dom = a <record> dom
        """
        # TODO : add <about> processing

        h = dom.getElementsByTagName("header")
        if len(h) == 0:
            h = ""
        else:
            h = self.get_HeaderXML(h[0])
            #h = unicode(h, self.default_encoding)

        m = dom.getElementsByTagName("metadata")
        if len(m) == 0:
            m = ""
        else:
            m = self.get_MetadataXML(m[0])
            #m = unicode(m, self.default_encoding)
        # a = self.get_AboutXML(dom.getElementsByTagName("about"))
        self.header = h
        self.metadata = m
        self.about = ""   # str(a)

    def get_HeaderXML(self, dom):
        """
        get header XML, dom to string
        pass in DOM node <header>
        """
        return dom.toxml(self.default_encoding)

    def get_MetadataXML(self, dom):
        """
        get metadata XML, dom to string
        pass in DOM node <metadata>
        """
        return dom.toxml(self.default_encoding)
        for section in dom.childNodes:
            # want just good section names, not whitespace, etc
                if hasattr( section, 'tagName'):
                    if section.tagName == "dc":
                        return section.toxml(self.default_encoding)

    def get_AboutXML(self, dom):
        """
        # TODO: about xml
        get about XML, dom to string
        pass in DOM node <about>
        """
        pass


    def get_HeaderList(self, tags=[]):
        """ """
        list = []
        dom = self.get_DOM('header')
        if dom == None: return list
        for element in dom.getElementsByTagName("header"):
            for child in element.childNodes:
                if hasattr( element, 'tagName') and child.tagName in tags:
                    list.append(self.get_DOMText(child.childNodes))
        return list

    def get_MetadataList(self, ns_name='', ns_qualifiers=[None], tags=[] ):
        """
        input list of tagnames to retrieve from tag and namespace
        returns list of strings of found data
        
        ns_name - name of tag to search eg, 'dc'
        ns_qualifiers - list of namespaces to search, eg [None, 'http://..']
        tags - list of tagnames (childNodes) in ns_name to collect
        """
        list = []
        dom = self.get_DOM('metadata')
        if dom == None: return list
        for ns in ns_qualifiers:
            for md in dom.getElementsByTagNameNS(ns, ns_name):
                for element in md.childNodes:
                    if hasattr( element, 'tagName') and element.tagName in tags:
                        list.append(self.get_DOMText(element.childNodes))
        return list