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

__doc__ = """ Zope Exist OAI Repository """


import string
from Globals import HTMLFile
from AccessControl import ClassSecurityInfo
from zOAIRepository import zOAIRepository
import DateTime

from zOAIExistNamespace import manage_addOAIExistNamespace, oai_dc_defaults, oai_lom_defaults

from zOAIExistTemplates import *
import zOAIExistToken
from pyOAIMH.OAIRepository import IdDoesNotExist, NoMetadataFormats, BadArgument, CannonDisseminateFormat, NoRecordsMatch
import xml.dom.minidom

manage_addOAIExistRepositoryForm = HTMLFile('dtml/manage_addOAIExistRepositoryForm', globals())

def manage_addOAIExistRepository(self,
                                 id="",
                                 title="OAI Exist Repository",
                                 existDAId='',
                                 existCollRoot = '',
                                 REQUEST=None,
                                 RESPONSE=None):
    """ method for adding a new OAI Exist Aggregator """

    if id == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20titre')
            return None
    if existCollRoot == '' or existDAId == '' or not hasattr(self, existDAId):
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20une%20collection%20et%20un%20eXistDAId%20correct')
            return None

    try:
        OAIO = zOAIExistRepository(id,
                                   title,
                                   0,
                                   existDAId,
                                   existCollRoot,
                                   )
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?updat_menu=1')


class zOAIExistRepository(zOAIRepository):
    """ """

    meta_type = 'Exist Open Archive Repository'

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
        {'label': 'Search',     
         'action': 'search' 
         },
        )

    manage_main = HTMLFile("dtml/manage_OAIExistRepositoryMainForm",globals())

    def __init__(self,
                 id,
                 title,
                 update_time,
                 existDAId,
                 existCollRoot,
                 ):
        """ """
        self.existDAId = existDAId
        self.existCollRoot = existCollRoot
        try:
            zOAIRepository.__init__(self, id, title, update_time)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            zOAIRepository.__init__.im_func(self, id, title, update_time)

    def manage_afterAdd(self, item, container):
        """ redef """
        # Collection creation for record save
        eda = self.get_eXistDA()
        if not eda or not self.getExistCollRoot():
            return
        eda.createColl(self.getExistCollRoot())
        zOAIExistRepository.inheritedAttribute("manage_afterAdd")(self, item, container)

##    def manage_beforeDelete(self, item, container):
##        """ redef """
##        # Collection delete
##        eda = self.get_eXistDA()
##        eda.delColl(self.getExistCollRoot())
##        zOAIExistRepository.inheritedAttribute("manage_beforeDelete")(self, item, container)

    def initialize(self):
        """
        initialize method for ExistAggregator
        """
        try:
            zOAIRepository.initialize(self)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            zOAIRepository.initialize.im_func(self)

        self.add_lomNamespace()

    def add_Catalog(self):
        """
        redefinition of add_Catalog method
        """
        return None

    def get_namespaceInfoByRootNode(self, rootNode):
        """
        return the namespace info dict given
        the rootNode
        """
        # put the dictionary together
        #  with the prefixes as keys
        nStor = self.get_myNamespaceStorage()
        for ns_obj in nStor.objectValues('Open Archive Exist Namespace'):
            if rootNode in ns_obj.get_nsPossibleRootNode():
                return ns_obj.get_nsDictionary()
        return {}

    def get_namespacePrefixByRootNode(self, rootNode):
        """
        return the namespace info dict given
        the rootNode
        """
        # put the dictionary together
        #  with the prefixes as keys
        nStor = self.get_myNamespaceStorage()
        for ns_obj in nStor.objectValues('Open Archive Exist Namespace'):
            if rootNode in ns_obj.get_nsPossibleRootNode():
                return ns_obj.id
        return ''

    def getExistCollRoot(self):
        """
        return the root collection for eXist storage
        """
        return self.existCollRoot       

    def get_eXistDA(self):
        """
        return the eXist DA
        """
        return getattr(self, self.existDAId)

    
    def doSearch(self, xquery_string, xml = 0, REQUEST = None, RESPONSE = None):
        """
        arg : xquery_string
        Submit the xquery_string on eXist DB
        """
        results = self.get_eXistDA().query(query = xquery_string)
        return results

    def add_dublinCoreNamespace(self):
        """
        add default oai_dc namespace
        required for all shared documents
        """

        # get default values
        dc_schema = oai_dc_defaults['schema']
        dc_namespace = oai_dc_defaults['namespace']
        dc_shortname = oai_dc_defaults['shortname']
        dc_description = oai_dc_defaults['description']
        dc_prefix = oai_dc_defaults['prefix']
        dc_rootNode = oai_dc_defaults['rootNode']
        dc_possibleRootNode = oai_dc_defaults['possibleRootNode']
        dc_idPath = oai_dc_defaults['idPath']
        dc_nsDeclaration = oai_dc_defaults['nsDeclaration']

        # get namespace storage location
        nStor = self.get_myNamespaceStorage()

        # add namespace
        manage_addOAIExistNamespace(nStor,
                                    ns_prefix=dc_prefix,
                                    ns_rootNode=dc_rootNode,
                                    ns_possibleRootNode=dc_possibleRootNode,
                                    ns_idPath=dc_idPath,
                                    ns_nsDeclaration=dc_nsDeclaration,
                                    ns_description=dc_description,
                                    ns_shortname=dc_shortname,
                                    ns_schema=dc_schema,
                                    ns_namespace=dc_namespace)


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
        lom_rootNode = oai_lom_defaults['rootNode']
        lom_possibleRootNode = oai_lom_defaults['possibleRootNode']
        lom_idPath = oai_lom_defaults['idPath']
        lom_nsDeclaration = oai_lom_defaults['nsDeclaration']

        # get namespace storage location
        nStor = self.get_myNamespaceStorage()

        # add namespace
        manage_addOAIExistNamespace(nStor,
                                    ns_prefix=lom_prefix,
                                    ns_rootNode=lom_rootNode,
                                    ns_possibleRootNode=lom_possibleRootNode,
                                    ns_idPath=lom_idPath,
                                    ns_nsDeclaration=lom_nsDeclaration,
                                    ns_description=lom_description,
                                    ns_shortname=lom_shortname,
                                    ns_schema=lom_schema,
                                    ns_namespace=lom_namespace)

    manage_preferences = HTMLFile("dtml/manage_OAIExistAggregatorPrefsForm",globals())

    def manage_OAIExistRepositoryPrefs(self,
                                       title,
                                       update_period,
                                       token_expiration,
                                       results_limit,
                                       existDAId,
                                       existCollRoot,
                                       REQUEST=None,
                                       RESPONSE=None):
        """ save preferences """
        self.title = title
        self.def_update = update_period
        self.token_expiration = token_expiration
        self.results_limit = results_limit
        self.existDAId = existDAId
        self.existCollRoot = existCollRoot
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')



    ###############################################
    ##
    ## Methods redefinition for eXistDB repository support
    ##
    ###############################################
    
    def get_ListMetadataFormats(self, args={}):
        """
        returns list of metadata formats 
           list is of namespace dictionary
           We can't give more than we have declared in Namespaces folder
        """
        the_list = []

        namespaces = self.get_myNamespaceStorage().objectValues('Open Archive Exist Namespace')
        
        if args.has_key('identifier'):
            # do search for item with identifier
            # return format types for it

            nsDeclaration = ""
            letSequence = ""
            resTemp = ""
            i = 1
            for ns in namespaces:
                infoDict = ns.get_nsDictionary()
                nsDeclaration += namespaceTemplate % infoDict['nsDeclaration']
                for prn in infoDict['possibleRootNode']:
                    letSequence += lmf_predicateTemplate % {
                        'indice':str(i),
                        'rootNode':prn,
                        'idPath':infoDict['idPath'],
                        'identifier':args['identifier'],
                        }
                    resTemp += lmf_resTemplate % str(i)
                    i = i+1
            my_query = queryTemplate_T % {
                'nsdeclaration':nsDeclaration,
                'mdlocation':self.existCollRoot,
                'letSequence':letSequence,
                'resTemplate':"<metadataPrefix>"+resTemp+"</metadataPrefix>",
                'xslFilter':xslExtractPrefix,
                }

            res = self.doSearch(xquery_string=my_query)

            prefixList = []
            for r in res.results:
                striped = r.xml.strip()
                if striped:
                    prefix = self.get_namespacePrefixByRootNode(striped)
                    if prefix and prefix not in prefixList:
                        prefixList.append(prefix)

            if prefixList == []:
                raise IdDoesNotExist, "OAI Error: idDoesNotExist"

            resultList = []
            for pref in prefixList:
                resultList.append(self.get_myNamespaceStorage()._getOb(pref).get_nsDictionary())
            return resultList

        else:
            # ask namespace definitions to take possible values
            for nsDeclaration in namespaces:
                the_list.append(nsDeclaration.get_nsDictionary())
        return the_list

    def get_GetRecord(self, args={}):
        """
        returns a record object in database from its identifier and metadataPrefix
        """
        if args.has_key('identifier') and args.has_key('metadataPrefix'):
            infoDict = self.get_myNamespaceStorage()._getOb(args['metadataPrefix']).get_nsDictionary()
            nsDeclaration = namespaceTemplate % infoDict['nsDeclaration']
            letSequence = ""
            resTemp = ""
            i = 1
            for prn in infoDict['possibleRootNode']:
                letSequence += gr_predicateTemplate % {
                    'indice':str(i),
                    'rootNode':prn,
                    'idPath':infoDict['idPath'],
                    'identifier':args['identifier'],
                    }
                resTemp += gr_resTemplate % str(i)
                i = i+1

            my_function = gr_function % {
                'identifier': args['identifier'],
                'oai_rootNode': infoDict['prefix'] + ':' + infoDict['rootNode'],
                'oai_ns': infoDict['prefix'] + '="' + infoDict['namespace'] + '"',
                'md_ns': infoDict['nsDeclaration'],
                }

            my_query = queryTemplate_F % {
                'nsdeclaration':nsDeclaration,
                'mdlocation':self.existCollRoot,
                'letSequence':letSequence,
                'resTemplate':"<records>"+resTemp+"</records>",
                'function': my_function,
                }

            res = self.doSearch(xquery_string=my_query)
            resultList = []
            for r in res.results:
                resultList.append(r.xml)

            # normally we have only one record but...
            try:
                resRecord = resultList[0]
            except:
                # could be idDoesNotExist or CannonDisseminateFormat error 
                raise IdDoesNotExist, "OAI Error: idDoesNotExist"

            header, metadata = re_extractRecord.findall(resRecord)[0]
        else:
            raise BadArgument, "OAI Error: badArgument"
        return ([[header, metadata, about_infos]], None)

    def get_ListRecords(self, args={}):
        """
        returns list of record objects in database
        """
        token = None
        old_token = None
        results_limit = self.results_limit
        # we need to get the args for the request
        #   either from our 'resumption token' or
        #   from our regular request dictionary
        if args.has_key('resumptionToken'):
            # get token using name and process arguments
            token_name = args['resumptionToken']
            old_token = self.get_myTokenStorage()._getOb(token_name, None)
            parent_id = old_token.id
            cursor = old_token.get_TokenArg('cursor')

            # put original query args in place (eg, set, from, metadataPrefix )
            #  plus things from zope
            args = old_token.get_RequestArgs()
            search_dict = {}
            for key, value in old_token.get_RequestArgs().items():
                search_dict[key] = value
        else:
            #if args.has_key('set'):
            #    search_dict['OAI_Set'] = args['set']
            cursor = 0
            parent_id = None

        rec_sent = cursor + results_limit

        metadataPrefix = args.get('metadataPrefix','')
        if not metadataPrefix:
            raise BadArgument, "OAI Error : badArgument"
        infoDict = self.get_myNamespaceStorage()._getOb(args['metadataPrefix']).get_nsDictionary()

        # do the search and setup variables
        #results = self.get_myCatalog().searchResults(search_dict)
        nsDeclaration = namespaceTemplate % infoDict['nsDeclaration']

        letSequence = []
        for prn in infoDict['possibleRootNode']:
            letSequence.append('$col//'+prn)
        letSequence = 'let $md1 := ' + '|'.join(letSequence)

        my_function = lr_function % {
            'idPath': infoDict['idPath'] ,
            'oai_rootNode': infoDict['prefix'] + ':' + infoDict['rootNode'],
            'oai_ns': infoDict['prefix'] + '="' + infoDict['namespace'] + '"',
            'md_ns': infoDict['nsDeclaration'],
            'about': about_infos,
            }

        my_query = queryTemplate_F % {
            'nsdeclaration':nsDeclaration,
            'mdlocation':self.existCollRoot,
            'letSequence':letSequence,
            'function': my_function,
            'start': str(cursor+1),
            'stop': str(rec_sent),
            }

        exist_results = self.get_eXistDA().fastquery(query=my_query, start=1, nbmax=self.results_limit+1)

        if len(exist_results)<1:
            raise NoRecordsMatch, "OAI Error : No records match"
        try:
            len_results = int(re_extractLenOfRecords.findall(exist_results)[0])
        except:
            raise NoRecordsMatch, "OAI Error: noRecordsMatch"
        results = re_extractRecords.findall(exist_results)
        the_list = []               # stores the records to send back
        record_count = 0            # index variable
        while (record_count + cursor) < len_results:
            # get search record and info
            record = results[record_count]
            record_count += 1     
            the_list.append(record)

            # check to see if we need to stop
            #   according to the size limit
            # if so, create a resumptionToken
            if record_count >= self.results_limit:
                token_args = {}
                token_args['cursor'] = record_count + cursor
                token_args['completeListSize'] = len_results
                date =  DateTime.DateTime() + (self.token_expiration / 1440.0)
                token_args['expirationDate'] = date.HTML4()

                # if we're done with entire list
                #   give empty id back
                records_done = record_count + cursor
                records_left = len_results - records_done
                if records_left == 0:
                    token_args['id'] = ""
                token = zOAIExistToken.manage_addOAIExistToken( self.get_myTokenStorage(), parent_id = parent_id, request_args = args.copy(), token_args = token_args )
                break
        else:
            # else for the while
            # need to add an empty resumption token if this is the end
            pass
        return (the_list, token)

    def do_ListRecords(self, xmldoc=None, listrecord=None, args={}):
        """
        create ListRecords XML response
        
        xmldoc - head of xml document
        identify - parent dom element for all of this stuff
        args - dict with args from Identify request
        """
        results, token = self.get_ListRecords(args)
        if len(results) == 0:
            raise NoRecordsMatch, "OAI Error: noRecordsMatch"

        # create <record> tags
        xml_declaration = '<?xml version="1.0" encoding="%s"?>\n' % self.default_encoding
        string_records = xml_declaration + "<ListRecords>" + "".join(results) + "</ListRecords>"

        resultDOM = xml.dom.minidom.parseString(string_records)
        for record in resultDOM.getElementsByTagName('record'):
            listrecord.appendChild(record)

        # add resumption token if necessary
        if token != None:
            resumption_token = xmldoc.createElement("resumptionToken")
            listrecord.appendChild(resumption_token)
            for key in ['expirationDate', 'completeListSize', 'cursor']:
                value = token.get_TokenArg(key)
                if value != None:
                    resumption_token.setAttribute(key, str(value))
            token_value = xmldoc.createTextNode(str(token.get_TokenArg('id')))
            resumption_token.appendChild(token_value)    

        return listrecord
