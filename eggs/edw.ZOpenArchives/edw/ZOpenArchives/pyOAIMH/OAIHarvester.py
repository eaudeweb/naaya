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

__doc__ = """ Class which implements the OAI harvester protocol """

import sys
import urllib2
import string
import lxml.etree # Create objects form xml elements
from urllib import urlencode
from datetime import datetime

from xml.sax import make_parser, saxutils
from xml.sax.handler import ContentHandler
import xml.dom.minidom

from CreateURL import CreateURL
from edw.ZOpenArchives.utils import utSortDictsListByKey

class ServerError(Exception): pass
class HTTPLibError(Exception): pass

class OAIHarvester:
    default_encoding = 'UTF-8'
    # gives tag path within XML structure to
    #   use to retrieve information. differences between
    #   OAI protocol versions
    def getDOMElementText(self, dom_node=None, encode=None):
        """

        DEPRECATED


        input is a DOM node

        returns text of node; encoded text if
          encode parameter is given
        """
        text = ""
        for node in dom_node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text = text + string.strip(node.data)
        if encode != None:
            text = text.encode(encode)
        return text.strip()

    def findDOMElements(self, dom_list=[], tag_path=[]):
        """

        DEPRECATED

        finds DOM elements in DOM trees by path
        path is a list of strings - eg, [ 'Adressbook','Adress','Person','Name']
        which corresponds to tag names in XML
        returns list of nodes which have this path, or [] for none
        """
        found_nodes = []
        if len(dom_list)==0 or len(tag_path)==0:
            return found_nodes

        # get next tag to search for
        tag_name = tag_path[0]
        new_path = tag_path[1:]
        for dom in dom_list:
##            for node in dom.getElementsByTagName(tag_name):
##                found_nodes.append(node)
            for node in dom.childNodes:
                if hasattr(node, 'tagName') and node.tagName == tag_name:
                    found_nodes.append(node)

        if len(new_path):
            found_nodes = self.findDOMElements(dom_list=found_nodes,tag_path=new_path)
        return found_nodes


    dompaths = {
        '1.1': {
          'protocolVersion':['Identify','protocolVersion'],
          'repositoryName':['Identify','repositoryName'],
          'baseURL':['Identify','baseURL'],
          'adminEmail':['Identify','adminEmail'],
          'description':['Identify','description'],
          'metadataFormat':['ListMetadataFormats','metadataFormat']
        },

        '2.0':{
          'protocolVersion':['OAI-PMH','Identify','protocolVersion'],
          'repositoryName':['OAI-PMH','Identify','repositoryName'],
          'baseURL':['OAI-PMH','Identify','baseURL'],
          'adminEmail':['OAI-PMH','Identify','adminEmail'],
          'description':['OAI-PMH','Identify','description'],
          'earliestDatestamp':['OAI-PMH','Identify','earliestDatestamp'],
          'deletedRecord':['OAI-PMH','Identify','deletedRecord'],
          'compression':['OAI-PMH','Identify','compression'],
          'granularity':['OAI-PMH','Identify','granularity'],
          'metadataFormat':['OAI-PMH','ListMetadataFormats','metadataFormat']
        }
    }

    def __init__(self, site_host, site_url):
        """ """
        # host and url for OAI server
        self.site_host = site_host
        self.site_url = site_url
        self.site_status = {
            'lastUpdate':None,
            'status': 'unknown',
            'lastRequest':None
        }

        # site_identify
        #   first group is must includes
        #   second is may include multiples
        self.site_identify = {
            'repositoryName':'',
            'baseURL':'',
            'protocolVersion':'1.1',
            'earliestDatestamp':'',
            'deletedRecord':'',
            'granularity':'',
            'adminEmail':[],

            'compression':None,
            'description':[]
        }

        # list of site's available metadata
        self.site_metadata = {
            'oai_dc': {
                'schema':'',
                'metadataNamespace':'',
                'metadataPrefix':'oai_dc'
            }
        }

        self.list_sets_selected = [] # List of keys that are selected
        self.list_sets_all = '1' # By default all sets are selected

    def initialize(self):
        """ """
        self.issue_Identify()
        self.issue_ListSets()

    def updateObject(self):
        """ updates older objects """
        self.site_status = {
            'lastUpdate':'',
            'status': '',
            'lastRequest':''
        }

    def handle_Error(self, errors):
        """
        put error in site
        returns 0 on OK,
        other for error codes
        """
        if len(errors) > 0:
            the_error = errors[0]
            return 1
        else:
            return 0

    def get_dompath(self, name, version=None):
        """
        give back the datapath list given
        name and version
        """
        if version==None:
            version = self.get_protocolVersion().strip()
        if not self.dompaths.has_key(version):
            return None
        paths = self.dompaths[version]
        if not paths.has_key(name):
            return None
        return paths[name]

    ###############################
    #### ATTRIBUTE ACCESSOR METHODS

    def get_siteHost(self):
        """ return site host """
        return self.site_host

    def set_siteHost(self, site_host):
        """ set site host """
        self.site_host=site_host

    def get_siteURL(self):
        """ return site url """
        return self.site_url

    def set_siteURL(self, site_url):
        """ set site url """
        self.site_url=site_url

    def get_siteStatus(self, section):
        """ return site status """
        if section not in self.site_status.keys():
            raise "incorrect seciton for siteStatus ", section
        return self.site_status[section]

    def set_siteStatus(self, section, value):
        """ """
        if section not in self.site_status.keys():
            raise "incorrect seciton for siteStatus ", section
        self.site_status[section] = value

    #### protocolVersion

    def set_protocolVersion(self, version=''):
        """ """
        self.site_identify['protocolVersion'] = version

    def get_protocolVersion(self):
        """ """
        if self.site_identify.has_key('protocolVersion'):
            return self.site_identify['protocolVersion']
        else:
            return None

    #### repositoryName

    def set_repositoryName(self, name=''):
        """ """
        self.site_identify['repositoryName'] = name

    def get_repositoryName(self):
        """ """
        if self.site_identify.has_key('repositoryName'):
            return self.site_identify['repositoryName']
        else:
            return None

    def set_baseURL(self, url=''):
        """ """
        self.site_identify['baseURL'] = url

    def get_baseURL(self):
        """ """
        if self.site_identify.has_key('baseURL'):
            return self.site_identify['baseURL']
        else:
            return None

    def set_earliestDatestamp(self, datestamp=''):
        """ """
        self.site_identify['earliestDatestamp'] = datestamp

    def get_earliestDatestamp(self):
        """ """
        if self.site_identify.has_key('earliestDatestamp'):
            return self.site_identify['earliestDatestamp']
        else:
            return None

    def set_deletedRecord(self, record=''):
        """ """
        self.site_identify['deletedRecord'] = record

    def get_deletedRecord(self):
        """ """
        if self.site_identify.has_key('deletedRecord'):
            return self.site_identify['deletedRecord']
        else:
            return None

    def set_granularity(self, granularity=''):
        """ """
        self.site_identify['granularity'] = granularity

    def get_granularity(self):
        """ """
        if self.site_identify.has_key('granularity'):
            return self.site_identify['granularity']
        else:
            return None

    def set_description(self, description_list=[]):
        """ """
        self.site_identify['description'] = description_list

    def get_description(self):
        """ """
        if self.site_identify.has_key('description'):
            return self.site_identify['description']
        else:
            return None

    def set_compression(self, compression=''):
        """ """
        self.site_identify['compression'] = compression

    def get_compression(self):
        """ """
        if self.site_identify.has_key('compression'):
            return self.site_identify['compression']
        else:
            return None

    def set_adminEmail(self, admin_list=[]):
        """ """
        self.site_identify['adminEmail']=admin_list

    def get_adminEmail(self):
        """ returns a list of email addresses """
        if self.site_identify.has_key('adminEmail'):
            return self.site_identify['adminEmail']
        else:
            return []

    def get_siteHost(self):
        """ """
        return self.site_host

    def do_updateSite(self):
        """
        get updates from site - Identify, ListMetadataFormats, ListRecords
        """

        # TODO: update will also need to check
        #   existing records for deletions on server, etc

        self.set_siteStatus('lastRequest', datetime.now().strftime('%Y-%m-%d %H:%M'))
        self.issue_Identify()
        self.issue_ListMetadataFormats()
        self.issue_ListSets()

        namespaces = getattr(self.aq_parent,'Namespaces')
        lNameSpaceMetaDataPrefix = []

        for nm in namespaces.objectValues():
            lNameSpaceMetaDataPrefix.append(nm.get_nsPrefix())

        for metadata_prefix in  self.site_metadata.keys():
            if metadata_prefix in lNameSpaceMetaDataPrefix:
                pass
                #self.issue_ListRecords( oai_metadataPrefix = metadata_prefix )

        self.set_siteStatus('lastUpdate', datetime.now().strftime('%Y-%m-%d %H:%M'))

    def issue_Identify(self):
        """ method to issue the 'oai/?verb=Identify' request """
        query_set = (
            ('verb', 'Identify', ),
        )
        response, data = self._get_url(query_set)
        if response.code == 200:
            self.set_siteStatus('status', 'Available')
            dom = xml.dom.minidom.parseString(data)
            self.handle_Identify(dom=dom)

        if response.code != 200:
            self.set_siteStatus('status', "%s (%s)" % (response.message, response.code) )
            raise ServerError

    def handle_Identify(self, dom=None):
        """
        we need to process the DOM from issue_Identify
        look for tags and put info in object attribs
        """
        # retrieve protocolVersion - single
        #   is chicken before egg scenario
        #   which type of protocol to use before getting protocol
        #   use getElementsByTagName because it will get everything

        node_list = dom.getElementsByTagName('protocolVersion')
        if len(node_list) != 1: raise "too many protocolVersions"
        for node in node_list:
            self.set_protocolVersion(self.getDOMElementText(node))

        # retrieve repositoryName - single
        path = self.get_dompath('repositoryName')
        node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        if len(node_list) != 1: raise "too many repositoryNames"
        for node in node_list:
            self.set_repositoryName(self.getDOMElementText(node))

        # retrieve baseURL - single
        path = self.get_dompath('baseURL')
        node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        if len(node_list) != 1: raise "too many baseURL"
        for node in node_list:
            self.set_baseURL(self.getDOMElementText(node))

        # retrieve adminEmail - multiple
        path = self.get_dompath('adminEmail')
        node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        admin_list = []
        for node in node_list:
            admin_list.append(self.getDOMElementText(node))
        self.set_adminEmail(admin_list)

        # description - multiple (optional)
        path = self.get_dompath('description')
        if path == None:
            self.set_description('N/A')
        else:
            desc_list = []
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            for node in node_list:
                desc_list.append(self.getDOMElementText(node))

            self.set_description(desc_list)

        ## these are for 2.0
        # retrieve earliestDatestamp - single
        path = self.get_dompath('earliestDatestamp')
        if path == None:
            self.set_earliestDatestamp('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            if len(node_list) != 1: raise "too many deletedRecords"
            for node in node_list:
                self.set_earliestDatestamp(self.getDOMElementText(node))

        # retrieve deletedRecord - single
        path = self.get_dompath('deletedRecord')
        if path == None:
            self.set_deletedRecord('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            if len(node_list) != 1: raise "too many deletedRecords"
            for node in node_list:
                self.set_deletedRecord(self.getDOMElementText(node))

        # granularity - single
        path = self.get_dompath('granularity')
        if path == None:
            self.set_granularity('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            if len(node_list) != 1: raise "too many granularity"
            for node in node_list:
                self.set_granularity(self.getDOMElementText(node))

        # compression - single (optional)
        path = self.get_dompath('compression')
        if path == None:
            self.set_compression('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            for node in node_list:
                self.set_compression(self.getDOMElementText(node))

    def handle_Resume(self, resumeToken ):
        """
        look for resumeToken field
        """
        if len(resumeToken.childNodes) > 0:
            return self.getDOMElementText(resumeToken)
        return None

    def issue_ListMetadataFormats(self, oai_identifier=None):
        """
        method to issue the 'oai/?verb=ListMetadataFormats'
        req args : none
        opt args : ID of record
        get list from site
          parse xml
          store results

        """
        query_set = (
            ('verb', 'ListMetadataFormats', ),
            ('identifier', oai_identifier, ),
        )
        response, data = self._get_url(query_set)
        self.set_siteStatus('status', 'Available')
        dom = xml.dom.minidom.parseString(data)
        #if self.handle_Error(dom.getElementsByTagName("error")) != 0:
        #    print "ERROR !! ", data
        # find <records> in DOM
        path = self.get_dompath('metadataFormat')
        metadom_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        self.handle_ListMetadataFormats(dom_list=metadom_list)

        if response.code != 200:
            self.set_siteStatus('status', "%s (%s)" % (response.msg, response.code) )
            raise ServerError

    def handle_ListMetadataFormats(self, dom_list=[]):
        """
        process metadata format DOM elements given from
          issue_ListMetadataFormats()
        get each DOM
           save tag info in dict
        """
        # reinitialize site_metadata before update
        self.site_metadata = {}
        for format in dom_list:
            dict = {}
            for element in format.childNodes:
                if hasattr(element, 'tagName'):
                    tag_name= element.tagName
                    tag_info = self.getDOMElementText(element, self.default_encoding)
                    dict[tag_name] = tag_info
            # TODO: check for existance of at least 'oai_dc'
            #  it's a minimum requirement in OAI spec
            self.site_metadata[dict['metadataPrefix']]=dict

    def issue_ListSets(self):
        """  method to issue the ?verb=ListSets"""
        query_set = (
            ('verb', 'ListSets', ),
        )
        response, data = self._get_url(query_set)
        if response.code == 200:
            tree = lxml.etree.fromstring(data)
            for element in tree:
                if 'error' in element.tag:
                    print "ERROR: List Sets\n\n", lxml.etree.tostring(data)
                    break
                elif 'ListSets' in element.tag:
                    self.handle_ListSets(element)
                    break

    def handle_ListSets(self, ListSets):
        """
        calls handle_addOAIRecord on all records found:
          this is a hook for a subclass to implement
        """
        sets = []
        for e in ListSets:
            sets.append({
                'spec': e[0].text,
                'name': e[1].text
            })
        self.list_sets = utSortDictsListByKey(sets, 'name', 0) #Order alphabeticaly

    def issue_ListRecords(self, oai_metadataPrefix, oai_from=None,
                          oai_until=None, oai_set=None, oai_setSpec=None ):
        """
        method to issue the 'oai/?verb=ListRecords&metadataPrefix=oai_dc'
        req args = metadataPrefix
        opt args = from, until, set (setSpec)
        exc args = resumptionToken
        get records from site
          create objects if necessary
          update ones which exist
          get next batch if more
        """
        # save this info until the end, so we can now
        #   a little about the request (metadataPrefix)
        self.current_request =  { 'verb':'ListRecords',
                                  'metadataPrefix':oai_metadataPrefix,
                                  'from':oai_from,
                                  'until':oai_until,
                                  'set':oai_set,
                                  'setSpec':oai_setSpec
                                  }
        url_obj = CreateURL( self.current_request )
        while 1:
            url = url_obj.getURL()
            try:
                returncode, returnmsg, headers, data = self.http_connect('?'+url)
                if returncode != 200:
                    break
                else:
                    self.set_siteStatus('status', 'Available')

                    dom = xml.dom.minidom.parseString(data)
                    if self.handle_Error(dom.getElementsByTagName("error")) != 0:
                        print "ERROR: List Records ", data
                        break

                    self.handle_ListRecords(dom.getElementsByTagName("ListRecords"))
                    resume_node = dom.getElementsByTagName("resumptionToken")
                    if resume_node == None or len(resume_node) == 0:
                        break

                    resumeToken_value = self.handle_Resume(resume_node[0])
                    if resumeToken_value == None:
                        break
                    url_obj.addProperty( { 'resumptionToken':resumeToken_value } )
                    url_obj.delProperty( ['metadataPrefix','from','until','set','setSpec'] )
            except:
                import traceback
                traceback.print_exc()
                self.set_siteStatus('status', 'Unavailable')
                raise HTTPLibError

        # outside of the WHILE
        self.current_request = None
        if returncode != 200:
            self.set_siteStatus('status', "%s (%s)" % (returnmsg,returncode) )
            raise ServerError

    def handle_ListRecords(self, ListRecords):
        """
        calls handle_addOAIRecord on all records found:
          this is a hook for a subclass to implement
        """
        if len(ListRecords) > 0:
            i = 0
            the_ListRecord = ListRecords[0]
            for record in the_ListRecord.getElementsByTagName("record"):
                i = i+1
                self.handle_addOAIRecord( dom=record )
                if i%10:
                    get_transaction().commit()

    def handle_addOAIRecord(self, record):
        """
        override this method
        get <record> DOM node
        depends on the database you have
        """


    def http_connect(self, get_url):
        """
        connect to site given GET url
        return connection results
        """
        h = httplib.HTTPConnection(self.site_host)
        h.connect()
        if sys.version_info[0] >= 2 and sys.version_info[1] >= 3:
            h.sock.settimeout(120.0)
        else:
            h.sock.set_timeout(120)

        h.request('GET', self.site_url + get_url)
        r1 = h.getresponse()
        returncode = r1.status
        returnmsg = r1.reason
        headers = r1.msg

        data = None
        if returncode == 200:  # OK
            data = r1.read()
        h.close()
        return ( returncode, returnmsg, headers, data )

    def _get_url(self, data = None):
        """ Return GET request to site_url, site_host
        Data as a list of tuples of key, values or a string"""
        if isinstance(data, (list, tuple)):
            data = urlencode(data)
        elif not isinstance(data, str):
            raise ValueError("Bad data")
        con = urllib2.urlopen("http://%s%s" % (self.site_host, self.site_url), data = data)
        return (con, con.read(), )
