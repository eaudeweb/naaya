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

"""
class which implements the OAI repository protocol  ie, a server
"""
            
import xml.dom.minidom
from types import UnicodeType

class OAIRepository:

    # grammar for requests, for arguments:
    #   0->optional, 1->required, 2->exclusive
    #

    OAI_Grammar = {
        'Identify' : {},
        'ListSets' : {}, 
        'ListMetadataFormats' : {'identifier' : 0},
        'GetRecord' : {'identifier' : 1,
                       'metadataPrefix' : 1},
        'ListRecords' : {'set' : 0,
                         'from' : 0,
                         'until' : 0,
                         'metadataPrefix' : 1,
                         'resumptionToken' : 2},
        'ListIdentifiers' : {'set' : 0,
                             'from' : 0,
                             'until' : 0,
                             'resumptionToken' : 2}
        }


    default_encoding = 'UTF-8'

    oai_ns = { 'xmlns' : "http://www.openarchives.org/OAI/2.0/",
                  'xmlns:xsi' : "http://www.w3.org/2001/XMLSchema-instance",
                  'xsi:schemaLocation': "http://www.openarchives.org/OAI/2.0/  http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
                  }

    def __init__(self):
        """ """
        self._repository=None   # dict for repository info

    def initialize(self):
        """
        """
        self._repository = {}

        # must include only one of these
        self.repositoryName('Repository Name')
        self.repositoryDomain('Repository Domain')
        self.baseURL('Base URL')
        self.protocolVersion('2.0')
        self.earliestDatestamp( 'empty' )  #  self.get_earliestDatestamp(
        self.deletedRecord('yes')
        self.granularity('YYYY-MM-DD')
        # must be at least one of these
        self.adminEmail([''])
        # may include multiple of these
        self.compression(['None'])
        self.description([''])
        # self.update_theRepository()

    ## functions for interface choices

    def get_GranularityOptions(self):
        """ """
        return ( [ ['Normal', 'YYYY-MM-DD'], ['Fine', 'YYYY-MM-DDThh:mm:ssZ'] ] )

    def get_DeletedRecordOptions(self):
        """ """
        return( [['Yes','persistent'], ['Partial','transient'],['No', 'no']] ) 

    ## methods to process incoming requests
    #
    def process_Request(self, args={}):
        """
        process incoming request
        - check arguments
        - handle OAI verb
        """
        try:
            self.check_Request(args)
        except BadArgument:
            return self.satisfy_Request(args, error="badArgument")
        except BadResumptionToken:
            return self.satisfy_Request(args, error="badResumptionToken")
        return self.satisfy_Request(args)

    def create_ErrorNode(self, xmldoc, error):
        """
        this creates the small error element in requests
        """
        element = xmldoc.createElement("error")
        element.setAttribute('code', error)
        return element

    def valid_ResumptionToken(self, token):
        """
        method to check if resumption token is valid
        token is string. return 0 or 1
        """
        # TODO
        return 1


    def check_Request(self, args={}):
        """
        checks request arguments against request grammar
        """
        # check to see if there is a verb
        if not args.has_key('verb'):
            raise BadArgument, "OAI Request Error: missing 'verb' parameter"
        verb = args['verb']

        # get grammar for verb
        if not self.OAI_Grammar.has_key(verb):
            raise BadArgument, "OAI Request Error: verb '%s' not implemented" % verb

        grammar = self.OAI_Grammar[verb]

        # check to make sure have proper args for verb
        exclusive = None
        for key in args.keys():
            if key == 'verb': continue
            if not grammar.has_key(key):
                raise BadArgument, "OAI Request Error: argument '%s' not applicable for verb '%s'" % (key,verb)
            if grammar[key] == 2:
                if exclusive != None:
                    raise BadArgument, "OAI Request Error: arguments %s and %s are exclusive" % ( key, exclusive)
                else:
                    exclusive = key

        # if an exclusive args are defined, we must have no others
        if exclusive != None and len(args) != 2:
            raise BadArgument, "OAI Request Error: argument %s is exclusive, no others allowed" % excl

        # check to make sure we have all required args for verb
        #  only do this if we have an exclusive
        if exclusive == None:
            for key in grammar.keys():
                if not args.has_key(key) and grammar[key]==1:
                    raise BadArgument, "OAI Request Error: argument %s required but not supplied" % key

        # need to check to make sure the resumptionToken is correct
        token = None
        if args.has_key('resumptionToken'):
            token = args['resumptionToken']
        if token != None and not self.valid_ResumptionToken(token):
            raise BadResumptionToken, "OAI Request Error: %s is an invalid resumptionToken " % token

    def satisfy_Request(self, args={}, error=None):
        """
        create the basic XML structure for the requests
        if have error, will send back error structure
        """
        # create xml document
        xmldoc = xml.dom.minidom.Document()

        # create <OAI-PMH> node - with attributes
        root = xmldoc.createElement("OAI-PMH")
        for key in self.oai_ns.keys():
            root.setAttribute( key, self.oai_ns[key] )
            xmldoc.appendChild(root)

        # create <response> node
        response = xmldoc.createElement("responseDate")
        response.appendChild( xmldoc.createTextNode(self.get_ResponseDate()) )
        root.appendChild(response)

        # create <request> node - with attributes
        request = xmldoc.createElement("request")
        for key in args.keys():
            request.setAttribute(key, args[key])
        request.appendChild(xmldoc.createTextNode(self.get_Request()))
        root.appendChild(request)

        if error != None:
            # output error message in response
            root.appendChild(self.create_ErrorNode(xmldoc, error))

        else:
            # process normally, first do a quick check
            #   to make sure that we have implemented the method
            #   which will handle the verb
            #   - eg, do_Identify, do_ListRecords
            #
            verb = args['verb']
            method_name = 'do_' + verb
            method = getattr(self, method_name, None)
            if method == None:
                raise "OAI Repository Error: method '%s' not implemented" % method_name

            # get DOM from method handler
            try:
                parent = method(xmldoc, xmldoc.createElement(verb), args)
                root.appendChild(parent)
            except NoRecordsMatch:
                root.appendChild(self.create_ErrorNode(xmldoc, "noRecordsMatch"))
        return xmldoc.toprettyxml(encoding=self.default_encoding, indent='',newl='')
        # return xmldoc.toxml(self.default_encoding)


    # helper functions for methods
    #  should be overridden
    #
    def get_Request(self):
        """
        returns string of request
        # eg, http://oai?verb=Identify
        """
        pass

    def get_ResponseDate(self):
        """
        returns a date string
        ISO format according to granularity iso8869
        """
        pass
    
    def get_earliestDatestamp(self):
        """
        get the date string for the earliest returns
        record a date string
        """
        pass

    def get_ListRecords(self, args={}):
        """
        for each record, a list
        in list, list of header, metadata, about
        each in a list
        """
        pass

    def get_GetRecord(self, args={}):
        """
        same format than get_ListRecords for one result
        """
        pass
    
    def get_ListMetadataFormats(self, args={}):
        """
        if there is an identifier, look for its metadata formats
        else get metadata options for whole repository
        """
        pass
    
    def update_theRepository(self, force_update=None):
        """ when changes need to be saved """
        pass


    ####
    #### METHODS TO PROCESS EACH TYPE OF REQUEST
    ####
    
    def do_Identify(self, xmldoc, identify, args={}):
        """
        create Identify XML response
        xmldoc - head of xml document
        identify - parent dom element for all of this stuff
        args - dict with args from Identify request
        """

        # add <repositoryName> info
        repository = xmldoc.createElement("repositoryName")
        repository.appendChild( xmldoc.createTextNode(self.repositoryName()) )
        identify.appendChild(repository)

        # add <baseURL> info
        baseURL = xmldoc.createElement("baseURL")
        baseURL.appendChild( xmldoc.createTextNode(self.baseURL()) )
        identify.appendChild(baseURL)

        # add <protocolVersion> info
        protocol = xmldoc.createElement("protocolVersion")
        protocol.appendChild( xmldoc.createTextNode(self.protocolVersion()) )
        identify.appendChild(protocol)

        # add <earliestDatestamp> info
        datestamp = xmldoc.createElement("earliestDatestamp")
        datestamp.appendChild( xmldoc.createTextNode(self.earliestDatestamp()) )
        identify.appendChild(datestamp)

        # add <deletedRecord> info
        deleted = xmldoc.createElement("deletedRecord")
        deleted.appendChild( xmldoc.createTextNode(self.deletedRecord()) )
        identify.appendChild(deleted)

        # add <granularity> info
        granularity = xmldoc.createElement("granularity")
        granularity.appendChild( xmldoc.createTextNode(self.granularity()) )
        identify.appendChild(granularity)

#        # add <adminEmail> info
        for email in self.adminEmail():
            admin = xmldoc.createElement("adminEmail")
            admin.appendChild( xmldoc.createTextNode(email) )
            identify.appendChild(admin)

        # TODO: compression tags
        # TODO: description tags

        return identify



    def do_ListMetadataFormats(self, xmldoc, listmeta, args={}):
        """
        create ListMetadataFormats XML response

        xmldoc - head of xml document
        listmeta - parent dom element for all of this stuff
        args - dict with args from ListMetadataFormats request
        """

        results = self.get_ListMetadataFormats(args)

        for ns_dict in results:
            # add <metadataFormat> element
            metaFormat = xmldoc.createElement("metadataFormat")
            listmeta.appendChild(metaFormat)

            # add <metadataPrefix> info
            metaPrefix = xmldoc.createElement("metadataPrefix")
            metaPrefix.appendChild( xmldoc.createTextNode( ns_dict['prefix']) )
            metaFormat.appendChild(metaPrefix)

            # add <schema> info
            metaSchema = xmldoc.createElement("schema")
            metaSchema.appendChild( xmldoc.createTextNode(ns_dict['schema']))
            metaFormat.appendChild(metaSchema)

            # add <metadataNamespace> info
            metaNamespace = xmldoc.createElement("metadataNamespace")
            metaNamespace.appendChild( xmldoc.createTextNode(ns_dict['namespace']))
            metaFormat.appendChild(metaNamespace)

        return listmeta


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
        xml_declaration = '<?xml version="1.0" encoding="%s"?>' % self.default_encoding
        for record_struct in results:
            record = xmldoc.createElement("record")
            header, metadata, about = record_struct
            # add <header> info
            if header != "":
                header = xml_declaration + header
                c_dom = xml.dom.minidom.parseString(header.encode(self.default_encoding))
                list = c_dom.getElementsByTagName("header")
                if len(list) > 0:
                    clone = list[0].cloneNode(1)
                    record.appendChild(clone)
            
            # add <metadata> info
            if metadata != "":
                metadata =  xml_declaration + metadata
                c_dom = xml.dom.minidom.parseString(metadata.encode(self.default_encoding))
                list = c_dom.getElementsByTagName("metadata")
                if len(list) > 0 :
                    clone = list[0].cloneNode(1)
                    record.appendChild(clone)

            # add <about> info
            if about != "":
                about = xml_declaration + about
                c_dom = xml.dom.minidom.parseString(about.encode(self.default_encoding))
                list = c_dom.getElementsByTagName("about")
                if len(list) > 0 :
                    clone = list[0].cloneNode(1)
                    record.appendChild(clone)
                
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

    def do_GetRecord(self, xmldoc, getrecord, args={}):
        """
        create Identify XML response
        
        xmldoc - head of xml document
        getrecord - parent dom element for all of this stuff
        args - dict with args from Identify request
        """
        results, token = self.get_GetRecord(args)
        if len(results) == 0:
            raise NoRecordsMatch, "OAI Error: noRecordsMatch"
        if len(results) != 1:
            results = [results[0]]
            #raise "OAI Repository Error: more than one record with id"

        # create <record> tags
        xml_declaration = '<?xml version="1.0" encoding="%s"?>' % self.default_encoding
        for record_struct in results:
            record = xmldoc.createElement("record")
            header, metadata, about = record_struct
            # add <header> info
            if header != "":
                header = xml_declaration + header
                if isinstance(header, UnicodeType ):
                    header = header.encode(self.default_encoding)
                c_dom = xml.dom.minidom.parseString(header)
                list = c_dom.getElementsByTagName("header")
                if len(list) > 0:
                    clone = list[0].cloneNode(1)
                    record.appendChild(clone)
            
            # add <metadata> info
            if metadata != "":
                metadata =  xml_declaration + metadata
                if isinstance(metadata, UnicodeType ):
                    metadata = metadata.encode(self.default_encoding)

                c_dom = xml.dom.minidom.parseString(metadata)
                list = c_dom.getElementsByTagName("metadata")
                if len(list) > 0 :
                    clone = list[0].cloneNode(1)
                    record.appendChild(clone)

            # add <about> info
            if about != "" and type(about) is type(""):
                about = xml_declaration + about
                if isinstance(about, UnicodeType ):
                    about = about.encode(self.default_encoding)
                c_dom = xml.dom.minidom.parseString(about)
                list = c_dom.getElementsByTagName("about")
                if len(list) > 0 :
                    clone = list[0].cloneNode(1)
                    record.appendChild(clone)
            getrecord.appendChild(record)
        return getrecord

    ####
    #### ATTRIBUTE ACCESSOR METHODS
    ####

    # these were made methods so that
    #    the inputs could be verified
    # if a value is passed in, the attribute gets set
    #    else the current attribute is returned
    
    def repositoryName(self, value=None):
        """ input a string """
        if value == None:
            return self._repository['repositoryName']
        self._repository['repositoryName'] = value

    def repositoryDomain(self, value=None):
        """ input a string """
        if value == None:
            return self._repository['repositoryDomain']
        self._repository['repositoryDomain'] = value

    def baseURL(self, value=None):
        """ input a string """
        if value == None:
            return self._repository['baseURL']
        self._repository['baseURL'] = value

    def protocolVersion(self, value=None):
        """ input a string """
        if value == None:
            return self._repository['protocolVersion']
        self._repository['protocolVersion'] = value

    def earliestDatestamp(self, value=None):
        """ input a date string """
        if value == None:
            return self._repository['earliestDatestamp']
        self._repository['earliestDatestamp'] = value
        
    def deletedRecord(self, value=None):
        """ input a string """
        if value == None:
            return self._repository['deletedRecord']
        self._repository['deletedRecord'] = value

    def granularity(self, value=None):
        """ input a string """
        if value == None:
            return self._repository['granularity']
        self._repository['granularity'] = value

    def adminEmail(self, value=None):
        """ input a list """
        if value == None:
            return self._repository['adminEmail']
        # TODO check if value is list
        # filter out empty entries
        self._repository['adminEmail'] = filter(None, value)

    def compression(self, value=None):
        """ input a list """
        if value == None:
            return self._repository['compression']
        self._repository['compression'] = filter(None, value)
        
    def description(self, value=None):
        """ input a list """
        if value == None:
            return self._repository['description']
        self._repository['description'] = filter(None, value)

##
##  EXCEPTION CLASSES
##    from OAI specification
##

class OAIError(Exception):
    """ base class for exceptions in this module """
    pass

class BadArgument(OAIError):
    """ raised when there are errors in arguments """
    pass

class BadResumptionToken(OAIError):
    """ raised when there is a bad token  """
    pass

class NoRecordsMatch(OAIError):
    """ raised when there are not records in search results """
    pass

class NoSetHierarchy(OAIError):
    """ raised when sets are requested, but not supported by repository """
    pass

class CannonDisseminateFormat(OAIError):
    """ raised when metadataPrefix format is not in object with identifier """
    pass

class IdDoesNotExist(OAIError):
    """ raised when value of the identifier argument is unknown or illegal """
    pass

class NoMetadataFormats(OAIError):
    """ raised when there are not metadata formats available for the specified item """
    pass
