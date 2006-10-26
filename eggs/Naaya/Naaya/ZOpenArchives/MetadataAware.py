# -*- coding: iso-8859-15 -*-
#################################################################################
#										#
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,		#
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez    		#
# Christian Martel								#
#	         								#
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


__doc__ = """ MetadataAware mix-in Class """

import urllib
import string
import DateTime

from Globals import HTMLFile
import xml.dom.minidom
import zOAIRecord
from pyOAIMH.MyXMLLib import MyXMLLib


#from Products.PTKBase.Formatage import Formatage

class MetadataAware(MyXMLLib):
    """

    _oai_state = 'shared' or 'unshared'
    _oai_metadata = '<xml string>' in oai format

    """

    default_encoding = 'UTF-8'
    
##  format_xsl = HTMLFile("xsl/format_xsl",globals())
    
##    def output_xml(self, viewFullText=0, REQUEST=None):
##        """ """
##        self.check_attributes()
##        my_xml = self._oai_metadata

##        html =  self.xml2html(my_xml, self.format_xsl( REQUEST, viewFullText=viewFullText))
##        return html


    def get_myZOAIServer(self):
        """
        returns the first ZOAIServer named zoai
        """
        return getattr(self, 'zoai', None)

        
    def get_MetadataList(self):
        """
        get list of possible metadata prefixes, eg, ['oai_dc', 'lom']
        """
        server = self.get_myZOAIServer()
        if server != None:
            return server.get_namespaceList('Prefix')
        return []

  
    def get_namespaceInfoByPrefix(self, prefix):
        """
        returns dictionary from server given prefix
        """
        # TODO: get operational with more than one server
        ns_dict = {}
        portal = self.getPortal()
        for server in portal.objectValues('Zope OAI Server'):
            ns_dict = server.get_namespaceInfoByPrefix(prefix)
        return ns_dict

                
    def oai_state(self):
        """ """
        state = "unshared"
        if hasattr(self, '_oai_state'):
            state = self._oai_state
        return state

    def oai_metadata(self):
        """
        returns entire object metadata XML if exists
        raises error if no metadata
        """
        # TODO : put in raise error
        meta = "No metadata"
        if hasattr(self, '_oai_metadata'):
            meta = self._oai_metadata
        else:
            raise
        
        return meta

    def check_attributes(self):
        """ """
        def_encode = 'UTF-8'
        if not hasattr(self, '_oai_state') or self._oai_state == None:
            self._oai_state = "unshared"
            
        if not hasattr(self, '_oai_metadata') or self._oai_metadata == None:
            self._oai_metadata = '<?xml version="1.0" encoding="%s" ?>\n<metadata></metadata>' % def_encode


    def reset_Metadata(self):
        """ """
        self._oai_metadata = None

    def get_metadataTypes(self):
        """
        returns list of object's metadata types
        """
        list = []
        # get existing object metadata
        self.check_attributes()
        
        meta_xml = self._oai_metadata     
        meta_dom = xml.dom.minidom.parseString(meta_xml)
        meta_tag = meta_dom.getElementsByTagName('metadata')[0]
        for e in meta_tag.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                list.append(e.tagName.encode(self.default_encoding))
                
        return list


    def get_metadataDOM(self, prefix = None):
        """
        returns object's metadata DOM given prefix
        raises error if doesn't exist
        prefix = 'oai_dc'
        """

        meta_xml = self._oai_metadata     
        meta_dom = xml.dom.minidom.parseString(meta_xml)
        meta_tag = meta_dom.getElementsByTagName('metadata')[0]
        for e in meta_tag.childNodes:
            if e.nodeType == e.ELEMENT_NODE and e.tagName == prefix:
                return e
                
        return None

    def has_metadata(self, prefix):
        """
        checks to see if object has
        metadata given a prefix.
        """
        # get existing object metadata
        self.check_attributes()
        meta_xml = self._oai_metadata     
        meta_dom = xml.dom.minidom.parseString(meta_xml)
        meta_tag = meta_dom.getElementsByTagName('metadata')[0]
        for e in meta_tag.childNodes:
            if e.nodeType == e.ELEMENT_NODE and e.tagName == prefix:
                return 1
        return 0

    def get_MetadataDictionary(self):
        """
        """
        # TODO: clean up error condition
        server = self.get_myZOAIServer()
        if server == None:
            raise "there are no zOAI Servers found at portal level"
        obj_data = {}
        obj_data['header_tags'] = h_tags = {}
        obj_data['metadata_tags'] = m_tags = {}

        site_domain = self.get_myZOAIServer().repositoryDomain()
        id =  'oai:'+ site_domain + ':' + '/' + self.absolute_url(1)
        h_tags['identifier'] = urllib.unquote(id)
        
        h_tags['datestamp'] = server.get_fixedDate(str(self.bobobase_modification_time()))

        m_tags['identifier'] = self.absolute_url()
        m_tags['title'] = self.Title()
        m_tags['description'] = self.Description()
        m_tags['subject'] = self.Subject()
        m_tags['type'] = self.Type()
        m_tags['date'] = server.get_fixedDate(str(self.bobobase_modification_time()))
        m_tags['creator'] = self.Creator()

        return obj_data


    manage_viewMetadataForm = HTMLFile("dtml/manage_viewMetadataForm",globals())

    def manage_viewMetadata(self, state="unshared", REQUEST=None, RESPONSE=None):
        """ """
        self.check_attributes()
        
        self._oai_state = state

        # add oai_dc if it isn't available
        #
        if self.oai_state() == "shared" and not self.has_metadata('oai_dc'):
            ns_dict = self.get_namespaceInfoByPrefix('oai_dc')
            obj_metadataDict = self.get_MetadataDictionary()
            xml = zOAIRecord.create_ObjectMetadata(self, obj_metadataDict, ns_dict= ns_dict)
            self.manage_addMetadata(m_name=ns_dict['prefix'], data_xml=xml)
        if self.getPortal() is None:    
            msg = 'manage_tabs_message=Saved%20'
        else:
            msg = 'portal_status_message=Enregistrement%20effectué'
        try:
            rop = self.rolesOfPermission('View')
            roles = []
            for r in rop:
                if r['selected'] == 'SELECTED':
                    roles.append(r['name'])
            if state == 'shared':
                try:
                    self.manage_permission('View', ['Anonymous'] + roles,1)
                except:
                    import traceback
                    traceback.print_exc()
            else:
                try:
                    roles.remove('Anonymous')
                    self.manage_permission('View', roles,1)
                except:
                    import traceback
                    traceback.print_exc()
        except:
            import traceback
            traceback.print_exc()
        self.reindex_object()
        
        RESPONSE.redirect(self.absolute_url() + '/manage_viewMetadataForm?' + msg )


    manage_addMetadataForm = HTMLFile("dtml/manage_addMetadataForm",globals())

    def manage_addMetadataFile(self, m_name='', file='', content_type='', REQUEST=None, RESPONSE=None):
        """ """
        self.check_attributes()
        msg = "your%20data%20has%20been%20updated."

        if file == "":
            msg = "missing%20filename"
            RESPONSE.redirect(self.absolute_url() + '/manage_viewMetadataForm?' + msg )
            
        data_xml = file.read()

        self.manage_addMetadata(m_name=m_name, data_xml=data_xml)

        RESPONSE.redirect(self.absolute_url() + '/manage_viewMetadataForm?' + msg )


    def manage_addMetadata(self, m_name='', data_xml=None):
        """ """
        self.check_attributes()
        # validate xml according with schema
        # get schema address
        # get schema
        # validate input file
        if not 1:
            msg = "not%20valid%20schema"
            RESPONSE.redirect(self.absolute_url() + '/manage_viewMetadataForm?' + msg )
        ##################
        # incorporate new metadata into existing metadata
        # get existing object metadata
        meta_xml = self._oai_metadata     
        meta_dom = xml.dom.minidom.parseString(meta_xml)
        meta_tag = meta_dom.getElementsByTagName('metadata')[0]

        # delete existing child which has same
        #   namespace if it exists

        # find all tags which exist and put in a list
        #   then remove them later - we can't edit a list
        #   while parsing over it
        # TODO: check for namespaces and such
        #       and other tag names
        remove_list = []
        for e in meta_tag.childNodes:
            if e.nodeType == e.ELEMENT_NODE and e.tagName == m_name:
                remove_list.append(e)

        # then remove the tags found
        for e in remove_list:
            meta_tag.removeChild( e )
        
        # create new container for metadata, eg <oai_dc>
        new_meta_node = meta_dom.createElement(m_name)
        meta_tag.appendChild(new_meta_node)

        # add metadata namespaces attributes
        new_meta_node.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        ns_dict = self.get_namespaceInfoByPrefix(prefix=m_name)
        for attr_info in [ ('schema','xsi:schemaLocation'),('namespace','xmlns')]:
            attr_key, attr_tag = attr_info
            new_meta_node.setAttribute(attr_tag, ns_dict[attr_key])
        
        to_meta_node = new_meta_node
        
        # find first element in new metadata
        #   to prepare for xml element copy
        data_dom = xml.dom.minidom.parseString(data_xml)
        from_meta_node = None
##       for e in data_dom.childNodes:
##            if e.nodeType == e.ELEMENT_NODE and e.tagName == m_name:
##                from_meta_node = e
##                break
        for e in data_dom.getElementsByTagName(m_name):
            if e.nodeType == e.ELEMENT_NODE and e.tagName == m_name:
                from_meta_node = e
                break
        if from_meta_node == None:
            print "tag not found"
            raise "ouch"

        # copy new metadata tags to object metadata
        for c in from_meta_node.childNodes:
            if c.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                c2 = c.cloneNode(1)
                to_meta_node.appendChild(c2)

        # TODO: add in encoding
        self._oai_metadata = meta_dom.toxml('UTF-8')


    manage_deleteMetadataForm = HTMLFile("dtml/manage_deleteMetadataForm",globals())

    def manage_deleteMetadata(self, m_name=None, REQUEST=None, RESPONSE=None):
        """ """
        self.check_attributes()
        msg = "manage_tabs_message=metadata%20for%20" + m_name + "%20hasbeendeleted"
        
        meta_xml = self._oai_metadata     
        meta_dom = xml.dom.minidom.parseString(meta_xml)
        meta_tag = meta_dom.getElementsByTagName('metadata')[0]
        # check that it has the name
        remove_list = []
        for e in meta_tag.childNodes:
            if e.nodeType == e.ELEMENT_NODE and e.tagName == m_name:
                remove_list.append(e)

        # then remove the tags found
        for e in remove_list:
            meta_tag.removeChild( e )

        # need to have 'oai_dc' as a minimum metadata
        #   so we need to unshare the document
        if m_name == 'oai_dc':
            self._oai_state = 'unshared'

        self._oai_metadata= meta_dom.toxml()
        RESPONSE.redirect(self.absolute_url() + '/manage_viewMetadataForm?' + msg )
