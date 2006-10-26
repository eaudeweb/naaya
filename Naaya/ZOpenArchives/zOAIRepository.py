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

__doc__ = """ Zope OAI Repository """

import DateTime
from DocumentTemplate.DT_Util import html_quote
import Globals
from Globals import HTMLFile, Persistent
from Products.ZCatalog.ZCatalog import ZCatalog
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
# from Products.PTKBase.PortalExtFile import manage_addPortalExtFile
from types import StringType, UnicodeType
import string
from pyOAIMH.OAIRepository import OAIRepository
import zOAIToken
import zOAINamespace
import App
import DateTime
from pyOAIMH.OAINamespace import oai_dc_defaults
import zOAINamespace
import urllib
from utils import latin1_to_ascii, utConvertLinesToList

##import StringIO

##from rdflib.TripleStore import TripleStore
##from rdflib.Literal import Literal
##from rdflib.Namespace import Namespace

class zOAIRepository(OAIRepository,App.Management.Navigation, Folder, Persistent, Implicit):
    """ """
    
    # meta_type = 'OVERRIDE'
    
    default_document = 'index_html'
    default_catalog = 'OAI_Catalog'
    default_tokenStorage = 'Tokens'
    default_namespaceStorage = 'Namespaces'
    # default_rdflib = 'RDFLib'
    default_encoding = 'UTF-8'
    
    manage_options= (   
        {'label': 'Contents',     
         'action': 'manage_main'
         },
        {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },
        
        {'label': 'Server Info',     
         'action': 'manage_repositoryInfo' 
         },
        {'label': 'Update',     
         'action': 'manage_repositoryUpdate' 
         },
        {'label': 'Search',     
         'action': 'search' 
         },
        )

    def __init__(self, id, title, update_time):
        """ """

        self.id = id
        self.title = title
        self.def_update = update_time
        self.results_limit = 100
        self.token_expiration = 5
        try:
            OAIRepository.__init__(self)
        except:
            OAIRepository.__init__.im_func(self)

    def initialize(self):
        """ """
        self.add_Catalog()
        self.add_resumptionTokenFolder()
        self.add_namespaceFolder()
        self.add_dublinCoreNamespace()
        try:
            OAIRepository.initialize(self)
        except:
            OAIRepository.initialize.im_func(self)
        self.baseURL(self.absolute_url())

        # add xron DTML method
        #
        #self.manage_addProduct['Xron'].manage_addXronDTMLMethod('RepositoryTimer', 'Xron event timer',
        #                                                   file='<dtml-call update_theRepository>', periodDays=(1.0), executeAt=DateTime.DateTime()+(1.0) )

        
        # add rdf library.
        # the_xml = """<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"></rdf:RDF>"""

##        file_obj = StringIO.StringIO("")
##        manage_addPortalExtFile(self, fn='RDFLib', title='RDFLib database',
##                                content_type='text/xml', file=file_obj)

    def index_html(self, REQUEST=None, RESPONSE=None):
        """
        process incoming OAI requests get args from request form
        """
##        self.the_request = "internal call"
##        if REQUEST.has_key('URL0'):
        self.the_request = REQUEST.URL0
        return self.process_Request(args=REQUEST.form)

    def get_myCatalog(self):
        """ get the OAI catalog object """
        return self._getOb(self.default_catalog)

    def get_myTokenStorage(self):
        """ get the OAI token  object """
        return self._getOb(self.default_tokenStorage)

    def get_myNamespaceStorage(self):
        """ """
        return self._getOb(self.default_namespaceStorage)

    def update_theRepository(self, force_update=0):
        """
        update the tokens
        """        
        cat = self.get_myCatalog()
        tStor = self.get_myTokenStorage()
        time_now = DateTime.DateTime().HTML4()
        results = cat.searchResults({ 'meta_type':'zOAI Token',
                                      'expiration':time_now,
                                      'expiration_usage':'range:max'})
        for token in results:
            tId = token.id
            tStor.manage_delObjects(ids=tId)
        # had to add this because Xron has some bug
        #    recatalog catalog
#        from Products.Xron.Schedule import ScheduleID
#        scheduler = getattr(self,ScheduleID)
#        scheduler.refreshCatalog(clear=1)

    def get_namespaceInfo(self, ns=""):
        """
        returns info for a particular namespaces
        given its name
        """
        nStor = self.get_myNamespaceStorage()
        ns_obj = nStor._getOb(ns)
        if ns_obj == None:
            return {}
        else:
            return ns_obj.get_nsDictionary()

    def get_namespaceInfoByPrefix(self, prefix):
        """
        return the namespace info dict given
        the namespace prefix
        """
        nStor = self.get_myNamespaceStorage()
        ns_obj = nStor._getOb(prefix)
        if ns_obj == None:
            return {}
        else:
            return ns_obj.get_nsDictionary()

    def XXget_namespace(self, ns):
        """ """
        ns_dict = None
        if self.namespaces.has_key(ns):
            ns_dict = self.namespaces[ns]
        return ns_dict

####
#### methods for RDLib stuff
####

##    def get_myRDFLib(self):
##        """ """
##        return self._getOb(self.default_rdflib)

##    def read_RDFLib(self):
##        """ """
##        ns_sn = Namespace("http://www.snee.com/ns/misc#")
##        ns_dc = Namespace("http://purl.org/dc/elements/1.1/")
##        ns_sd = Namespace("http://www.snee.com/docs/")
        
##        # Create storage object for triples.
##        store = TripleStore()
        
##        # Add triples to store.
##        store.add((ns_sd["d1001"], ns_dc["title"], Literal("Sample Acrobat document")))
##        store.add((ns_sd["d1002"], ns_dc["format"], Literal("PDF")))
##        store.add((ns_sd["d1003"], ns_dc["creator"], Literal("Billy Shears")))

##        docID = "d1003"
##        print "Information about document " + docID + ":"
##        for docInfo in store.predicate_objects(ns_sd[docID]):
##            print docInfo

##        store.save()


    ####
    #### OVERLOADED METHODS OF OAI_REPOSITORY
    ####
    
    def get_Request(self):
        """
        returns the request for the return
        """
        try:
            return self.the_request
        except AttributeError:
            return "%s/index_html" % self.aq_parent.absolute_url(0)

    def get_earliestDatestamp(self):
        """
        get earliest datestamp in repository
        return string of date
        earliest date in repository.
        if repository is empty, return today's date
        """
        results = self.get_myCatalog().searchResults({ 'meta_type':'Open Archive Record',
                                                       'sort_on':'OAI_Date',
                                                       'sort_order':'reverse' })
        if len(results) == 0:
            return self.get_fixedDate()
        else:
            return self.get_fixedDate( results[0].OAI_Date )

    def get_ResponseDate(self, date=None):
        """
        get response date for request - current date
        """
        return self.get_fixedDate()

    def get_fixedDate(self, date_str=None):
        """
        return fixed date string depending on
        granularity of server
        """
        if date_str == None:
            date = DateTime.DateTime()
        else:
            date = DateTime.DateTime(date_str)
        granularity = self.granularity()
        if granularity == 'YYYY-MM-DD':
            d_str = str( date.strftime("%Y-%m-%d") )
        elif granularity == 'YYYY-MM-DDThh:mm:ssZ':
            d_str = str( date.HTML4() )
        else:
            raise "Unknown granularity: '%s'", granularity 
        return d_str

    def get_GetRecord(self, args={}):
        """
        return a record in a list to be get_ListRecords compatible
        """
        return self.get_ListRecords(args)

    def get_ListRecords(self, args={}):
        """
        returns list of record objects in database
        """
        token = None
        old_token = None

        search_dict = {'meta_type':'Open Archive Record'}
        search_dict['sort_limit'] = self.results_limit

        # we need to get the args for the request
        #   either from our 'resumption token' or
        #   from our regular request dictionary
        #
        if args.has_key('resumptionToken'):
            # get token using name and process arguments
            token_name = args['resumptionToken']
            old_token = self.get_myTokenStorage()._getOb(token_name, None)
            parent_id = old_token.id
            cursor = old_token.get_TokenArg('cursor')
            rec_sent = cursor + self.results_limit
            # put original query args in place (eg, set, from, metadataPrefix )
            #  plus things from zope
            for key, value in old_token.get_RequestArgs().items():
                search_dict[key] = value
        else:
            #if args.has_key('set'):
            #    search_dict['OAI_Set'] = args['set']
            rec_sent = cursor = 0
            parent_id = None
            if args.has_key('identifier'):
                search_dict['OAI_Identifier'] = args['identifier']
        # do the search and setup variables
        results = self.get_myCatalog().searchResults(search_dict)
        the_list = []               # stores the records to send back
        record_count = 0            # index variable
        len_results = len(results)  # let's count 'em once

        while (record_count + rec_sent) < len_results:

            # get search record and info
            record = results[rec_sent+record_count]
            record_count += 1     

            header = getattr(record, 'header', "")
            metadata = getattr(record, 'metadata', "")
            about = getattr(record, 'about', "")
            the_list.append( [header, metadata, about] )
            # check to see if we need to stop
            #   according to the size limit
            # if so, create a resumptionToken
            if record_count >= self.results_limit:
                token_args = {}
                token_args['cursor'] = rec_sent
                token_args['completeListSize'] = len_results
                date =  DateTime.DateTime() + (self.token_expiration / 1440.0)
                token_args['expirationDate'] = date.HTML4()
                # if we're done with entire list
                #   give empty id back
                records_done = record_count + rec_sent
                records_left = len_results - records_done
                if records_left == 0:
                    token_args['id'] = ""
                token = zOAIToken.manage_addOAIToken( self.get_myTokenStorage(), parent_id = parent_id, request_args = args, token_args = token_args )
                break
        else:
            # else for the while
            # need to add an empty resumption token if this is the end
            pass
        return (the_list, token)

    def get_ListMetadataFormats(self, args={}):
        """
        returns list of metadata formats in catalog
          list is of namespace dictionary
        """
        the_list = []
        if args.has_key('identifier'):
            # do search for item(s) with identifier
            # return format types for them
            search_dict = {'meta_type':'Open Archive Record'}
            search_dict['OAI_Identifier'] = args['identifier']
            if len(results) == 0:
                raise IdDoesNotExist, "OAI Error: idDoesNotExist"
            results = self.get_myCatalog().searchResults(search_dict)
            for record in results:
                ns_prefix = record.OAI_MetadataFormat()
                the_list.append(  self.get_namespaceInfoByPrefix(ns_prefix) )
            if len(the_list) == 0:
                raise NoMetadataFormats, "OAI Error: noMetadataFormats"
        else:
            # ask catalog for its values for OAI_MetadataFormats
            results = self.get_myCatalog().uniqueValuesFor('OAI_MetadataFormat')    
            for ns_prefix in results:
                the_list.append( self.get_namespaceInfoByPrefix(ns_prefix) )
        return the_list

    def valid_ResumptionToken(self, token_name):
        """
        method to check if resumption token is valid
        token is the name of the token
        """
        # check in resumption token folder for object with this id
        if self.get_myTokenStorage()._getOb(token_name, None) != None:
            return 1
        else:
            return 0

    ####
    #### INITIALIZATION STUFF
    ####

    def add_Catalog(self):
        """
        adds a default catalog with id
        """
        catalog_id = self.default_catalog
        self.manage_addProduct['ZCatalog'].manage_addZCatalog(catalog_id, 'Default catalog')
        cat = self._getOb(catalog_id)
        self.add_Lexicon(cat)
        self.add_Indexes(cat)
        self.add_MetadataColumns(cat)

    def add_resumptionTokenFolder(self):
        """ """
        self.manage_addProduct['OFSP'].manage_addFolder(self.default_tokenStorage, 'resumptionToken storage')

    def add_namespaceFolder(self):
        """ """
        self.manage_addProduct['OFSP'].manage_addFolder(self.default_namespaceStorage, 'Namespace storage')

    def add_dublinCoreNamespace(self):
        """
        add default oai_dc namespace
        required for all shared documents
        """
        dc_schema = oai_dc_defaults['schema']
        dc_namespace = oai_dc_defaults['namespace']
        dc_shortname = oai_dc_defaults['shortname']
        dc_description = oai_dc_defaults['description']
        dc_prefix = oai_dc_defaults['prefix']

        # get namespace storage location
        nStor = self.get_myNamespaceStorage()

        # add namespace
        zOAINamespace.manage_addOAINamespace(nStor, ns_prefix=dc_prefix, ns_description=dc_description, ns_shortname=dc_shortname, ns_schema=dc_schema, ns_namespace=dc_namespace)

    def add_lomNamespace(self):
        """
        add lom namespace
        not required but usefull
        """
        # get default values
        lom_schema = oai_lom_defaults['schema']
        lom_namespace = oai_lom_defaults['namespace']
        lom_shortname = oai_lom_defaults['shortname']
        lom_description = oai_lom_defaults['description']
        lom_prefix = oai_lom_defaults['prefix']

        # get namespace storage location
        nStor = self.get_myNamespaceStorage()

        # add namespace
        zOAINamespace.manage_addOAINamespace(nStor, ns_prefix=lom_prefix, ns_description=lom_description, ns_shortname=lom_shortname, ns_schema=lom_schema, ns_namespace=lom_namespace)


    def add_Lexicon(self, cat):
        """
        adds default lexicon to 'Lexicon' id
        """

        elem = []
        wordSplitter = Empty()
        wordSplitter.group = 'Locale Aware Word Splitter'
        wordSplitter.name = 'Locale Aware Word Splitter'

        caseNormalizer = Empty()
        caseNormalizer.group = 'Case Normalizer'
        caseNormalizer.name = 'Case Normalizer'

        stopWords = Empty()
        stopWords.group = 'Stop Words'
        stopWords.name = 'Remove listed and single char words'

        accentRemover = Empty()
        accentRemover.group = 'Accent Normalizer'
        accentRemover.name = 'Accent Normalizer'

        elem.append(wordSplitter)
        elem.append(caseNormalizer)
        elem.append(stopWords)
        elem.append(accentRemover)
        try:
            cat.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Default Lexicon', elem)
        except:
            pass

    def add_Indexes(self, cat):
        """
        OVERRIDE - have own set of indexes
        """
        # general searching - from web form
        cat.addIndex('OAI_Date', 'FieldIndex')
        #cat.addIndex('OAI_Date', 'DateIndex')
        pass
       
    def add_MetadataColumns(self, cat):
        """
        OVERRIDE - have own set of metadata
        """
        # cat.manage_addColumn('id')
        pass

    ####
    #### OBJECT MANAGEMENT STUFF
    ####

    style_css   = HTMLFile("css/style_css",globals())

    search = HTMLFile("dtml/search_OAIRepositoryForm",globals())
    advsearch = HTMLFile("dtml/advsearch_OAIRepositoryForm",globals())
    portal_OAISearchForm = HTMLFile("dtml/portal_OAISearchForm",globals())
    portal_AdvSearchForm = HTMLFile("dtml/portal_AdvSearchForm",globals())
    xslOAIResultSearch = HTMLFile("xsl/xslOAIResultSearch",globals())
    portal_OAISearchResult = HTMLFile("dtml/portal_OAISearchResult",globals())
    
    def manage_searchXML(self, title="", text="", REQUEST=None, RESPONSE=None):
        """
        return
        """
        xml_response = '<?xml version="1.0" encoding="%s"?>\n' % self.default_encoding
        xml_response += "<searchresults>\n"
        xml_response += "  <parameters>\n"
        xml_response += "    <title>%s</title>\n" % html_quote(unicode(self.textCorrection(title), self.default_encoding ))
        xml_response += "    <text>%s</text>\n" % html_quote(unicode(self.textCorrection(text),self.default_encoding ))
        xml_response += "  </parameters>\n"

        if title=="" and text=="":
            results = []
        else:
            results = self.get_myCatalog().searchResults({ 'meta_type':'Open Archive Record',
                                                           'OAI_Title':latin1_to_ascii(title),
                                                           'OAI_Fulltext':latin1_to_ascii(text)
                                                           })
        xml_response += "  <records number=\"%s\">\n" % len(results)
        l = []
        for record in results:
            xml_tmp = ""
            xml_tmp += "    <record>\n"
            xml_tmp += "      <title>%s</title>\n" % html_quote(unicode(record.OAI_Title, self.default_encoding))
            xml_tmp += "      <author>%s</author>\n" % html_quote(unicode( record.dc_author, self.default_encoding))
            xml_tmp += "      <type>%s</type>\n" % html_quote(unicode( record.dc_type, self.default_encoding))
            xml_tmp += "      <creator>%s</creator>\n" % html_quote(unicode( record.dc_creator, self.default_encoding))
            xml_tmp += "      <description>%s</description>\n" % html_quote(unicode(record.dc_description, self.default_encoding))
            xml_tmp += "      <source>%s</source>\n" % urllib.quote(unicode(record.dc_identifier, self.default_encoding))
            xml_tmp += "      <identifier>%s</identifier>\n" % record.OAI_Identifier
            xml_tmp += "    </record>\n"
            l.append(xml_tmp)
        xml_response += string.join(l)
        xml_response += "  </records>\n"
        xml_response += "</searchresults>"
        return xml_response

    def searchHTML(self, title="", text="", author="", REQUEST=None, RESPONSE=None):
        """ """
        my_cat = self.get_myCatalog()
        if title=="" and text=="":
            results = []
        else:
            results = my_cat.searchResults({ 'meta_type':'Open Archive Record',
                                                           'OAI_Title':latin1_to_ascii(title),
                                                           'OAI_Fulltext':latin1_to_ascii(text)
                                                           })
        records = []
        for record in results:
            x = my_cat.getobject(record.data_record_id_)
            records.append(x)
        return records

    def getRecords(self):
        """
        return
        """
        results = self.get_myCatalog().searchResults({ 'meta_type':'Open Archive Record',})
        return results

    searchXML = manage_searchXML

    def manage_advSearchXML(self, REQUEST=None, RESPONSE=None):
        """
        return
        """
        searchDict = {'meta_type':'Open Archive Record'}
        requestDict = REQUEST.form
        for param in requestDict.keys():
            # search for dc_ and lom_
            if param[:3]=='dc_' or param[:4]=='lom_' or param[:4]=='OAI_':
                searchDict[param] = latin1_to_ascii(requestDict[param])
        xml_response = '<?xml version="1.0"  encoding="%s" ?>\n' % self.default_encoding
        xml_response += "<searchresults>\n"
        xml_response += "  <parameters>\n"
        for param in searchDict.keys():
            if param=='meta_type':
                continue
            xml_response += "    <%s>%s</%s>\n" % (param, html_quote(unicode(self.textCorrection(searchDict[param])),self.default_encoding), param)
        xml_response += "  </parameters>\n"
        results = self.get_myCatalog().searchResults(searchDict)
        xml_response += "  <records number=\"%s\">\n" % len(results)
        l = []
        for record in results:
            xml_tmp = ""
            xml_tmp += "    <record>\n"
            xml_tmp += "      <title>%s</title>\n" % html_quote(unicode(record.OAI_Title, self.default_encoding))
            xml_tmp += "      <author>%s</author>\n" % html_quote(unicode(record.dc_author, self.default_encoding))
            xml_tmp += "      <type>%s</type>\n" % html_quote(unicode(record.dc_type, self.default_encoding))
            xml_tmp += "      <creator>%s</creator>\n" % html_quote(unicode(record.dc_creator, self.default_encoding))
            xml_tmp += "      <description>%s</description>\n" % html_quote(unicode(record.dc_description, self.default_encoding))
            xml_tmp += "      <source>%s</source>\n" % urllib.quote(unicode(record.dc_identifier, self.default_encoding))
            xml_tmp += "      <identifier>%s</identifier>\n" % record.OAI_Identifier
            xml_tmp += "    </record>\n"
            l.append(xml_tmp)
        xml_response += string.join(l)
        xml_response += "  </records>\n"
        xml_response += "</searchresults>"
        return xml_response

    advSearchXML = manage_advSearchXML  

    # manage preferences is overridden
    # in the other classes
    #
    manage_preferences = HTMLFile("dtml/manage_OAIRepositoryPrefsForm",globals())
    def manage_OAIRepositoryPrefs(self, title, update_time, repositoryName,
                                  adminEmailList, autopublishRoles,
                                  REQUEST=None, RESPONSE=None):
        """ save preferences """
        self.title = title
        self.def_update = update_time
        self.def_autopublishRoles = autopublishRoles
        self.adminEmail(adminEmailList)
        self.repositoryName(repositoryName)
        # TODO, only if necessary
        self.update_theRepository()
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')

    manage_repositoryInfo = HTMLFile("dtml/manage_OAIRepositoryInfoForm",globals())
    def manage_OAIRepositoryInfo(self,  repositoryDomain,
                                 deletedRecord, granularity, 
                                 REQUEST=None, RESPONSE=None):
        """
        save server information
        a change will cause the database to be rebuilt
        """
        # baseURL, protocolVersion can't be changed
        self.repositoryDomain(repositoryDomain)
        # self.earliestDatestamp( earliestDatestamp)
        self.deletedRecord(deletedRecord) 
        self.granularity(granularity)

        # update datestamp in case granularity has changed
        self.earliestDatestamp(self.get_earliestDatestamp())

        # self.compression( compression)
        # self.description( description)
        self.commit_Changes()
        RESPONSE.redirect(self.absolute_url() + '/manage_repositoryInfo?manage_tabs_message=Settings%20saved')

    manage_repositoryUpdate = HTMLFile("dtml/manage_ZopeOAIRepositoryUpdateForm",globals())

    def manage_ZopeOAIServerUpdate(self, REQUEST=None, RESPONSE=None):
        """ """
        force_update = 0
        if REQUEST.has_key('force_update'):
            force_update = 1
        self.update_theRepository(force_update=force_update)
        RESPONSE.redirect(self.absolute_url() + '/manage_repositoryUpdate?manage_tabs_message=Server%20has%20been%20updated')

    def commit_Changes(self):
        """ """
        self._p_changed = 1

    ###### Pour régler les problèmes d'encodage en utf-8 ###########################
    def textCorrection(self,text=''):
        """ Script for xml file correction due to lot of errors in the xml result """
        for c in text:
            if ord(c)>=224:
                text = string.replace(text,c,'&#'+str(ord(c))+';')
        return text

##########
# empty class for creation of catalog initialization
#

class Empty: pass


from Products.ZCTextIndex.ILexicon import ILexicon
from Products.ZCTextIndex.PipelineFactory import element_factory

class AccentNormalizer:
    
    def process(self, lst):
        return [latin1_to_ascii(w) for w in lst]
    
if 'Accent Normalizer' not in element_factory.getFactoryGroups():    
    element_factory.registerFactory('Accent Normalizer',
                                    'Accent Normalizer',
                                    AccentNormalizer)

class LocaleAwareSplitter:

    import re
    rx = re.compile(r"\w+", re.UNICODE )
    rxGlob = re.compile(r"\w+[\w*?]*",re.UNICODE ) # See globToWordIds() above
    
    def process(self, lst):
        result = []
        for s in lst:
            u = unicode(s,'utf-8')
            t = self.rx.findall(u)
            result += t
        return result

    def processGlob(self, lst):
        result = []
        for s in lst:
            result += self.rxGlob.findall(s)
        return result
    
if 'Locale Aware Word Splitter' not in element_factory.getFactoryGroups():
    element_factory.registerFactory('Locale Aware Word Splitter',
                                    'Locale Aware Word Splitter',
                                    LocaleAwareSplitter)
