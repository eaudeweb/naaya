from datetime import datetime, timedelta
from urllib import quote
from oaipmh import server, metadata
from oaipmh.error import (NoSetHierarchyError, BadResumptionTokenError,
                          IdDoesNotExistError, CannotDisseminateFormatError)

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from App.ImageFile import ImageFile
import DateTime
from Missing import Missing
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope import interface, schema

from ZCatalogHarvester import ZCatalogHarvester
from OAIRepository import OAIRepository
from OAIRecord import OAIRecord
from OAIToken import manage_addOAIToken

from interfaces import IOAIServer
from utils import create_object, process_form, clean_xml

#possible token keys
token_keys = ['metadataPrefix', 'offset', 'set', 'from', 'until']
def unserialize_token(token):
    "Split comma separated token and return a dictionary with values"
    token_dict = {}
    if isinstance(token, str):
        token_values  = token.split(',')
        for key in token_keys:
            try:
                token_dict[key] = token_values[token_keys.index(key)]
            except IndexError:
                token_dict[key] = ''
        return token_dict
    raise BadResumptionTokenError, 'unserialization failed'

def serialize_token(token):
    "Create a comma separated string for inclusion in the URL"
    if isinstance(token, dict):
        return ','.join([str(token.get(key, '')) for key in token_keys])
    raise BadResumptionTokenError, "dict expected"

manage_addOAIServerForm = PageTemplateFile('zpt/manage_addOAIServerForm',
                                           globals())
def manage_addOAIServer(self, id='', REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)
    try:
        ob = create_object(self, OAIServer, id)
        process_form(ob, IOAIServer, form_data)
        ob.initialize()
    except Exception, e:
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=%s' % quote(str(e)))
        else:
            raise Exception(e)
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/manage_main?update_menu=1')

class OAIServer(OAIRepository):
    """ OAI2 Server implementation """
    interface.implements(IOAIServer)

    meta_type = 'OAI Server'
    all_meta_types = ({
        'name': ZCatalogHarvester.meta_type,
        'action':
            '/manage_addProduct/ZOpenArchives/manage_addZCatalogHarvesterForm',
        'product': ZCatalogHarvester.meta_type
        },
    )
    security = ClassSecurityInfo()

    stylesheet = ImageFile('www/celestial.xsl', globals())
    stylesheet.content_type = '	application/xml'

    def initialize(self):
        """ Create a oaipmh server to responde to OAI requests"""
        metadata_registry = metadata.MetadataRegistry()
        metadata_registry.registerWriter('oai_dc', server.oai_dc_writer)
        self.server = server.ServerBase(self, metadata_registry)
        self.base_url = self.absolute_url()
        super(OAIServer, self).initialize()

    security.declarePublic('index_html')
    def index_html(self, REQUEST=None, **kwargs):
        """ This is page that responds to the OAI2 requests. Uses PyOAI """
        if REQUEST is not None:
            response = self.server.handleRequest(REQUEST.form)
        else:
            response = self.server.handleRequest(kwargs)

        REQUEST.RESPONSE.setHeader('content-type', 'application/xml')
        #Add a stylesheet
        return response.replace("<?xml version='1.0' encoding='UTF-8'?>",
                         "<?xml version='1.0' encoding='UTF-8'?>\n"
                         "<?xml-stylesheet type='text/xsl'"
                         " href='" + self.absolute_url() + "/stylesheet'?>")

    security.declareProtected(view_management_screens, 'add_indexes')
    def add_indexes(self, catalog):
        """ Add indexes for catalog

        XXX:
        These indexes are not used currently because the OAI Record now
        contains 2 attributes: header and metadata.

        """

        catalog.addIndex('path', 'PathIndex')
        try:
            catalog.addIndex('meta_type', 'FieldIndex')
        except:
            pass
        catalog.addIndex('expiration', 'FieldIndex')
        catalog.addIndex('last_update', 'FieldIndex')

        # general searching - from web form
        catalog.addIndex('h_identifier', 'FieldIndex')
        catalog.addIndex('h_datestamp', 'DateIndex')
        catalog.addIndex('h_setspec', 'KeywordIndex')
        catalog.addIndex('h_deleted', 'FieldIndex')

        # dc search indexes
        catalog.addIndex('m_title', 'KeywordIndex')
        catalog.addIndex('m_creator', 'KeywordIndex')
        catalog.addIndex('m_author', 'KeywordIndex')
        catalog.addIndex('m_subject', 'KeywordIndex')
        catalog.addIndex('m_description', 'KeywordIndex')
        catalog.addIndex('m_date', 'KeywordIndex')

    security.declareProtected(view_management_screens, 'add_metadata')
    def add_metadata(self, catalog):
        """ Adding metadata columns """
        #Add id and title columns if not present
        try:
            catalog.manage_addColumn('id')
        except:
            pass
        try:
            catalog.manage_addColumn('title')
        except:
            pass
        # ZOAI specific columns
        catalog.manage_addColumn('header')
        catalog.manage_addColumn('metadata')
        catalog.manage_addColumn('about')
        catalog.manage_addColumn('meta_type')
        catalog.manage_addColumn('h_datestamp')

    security.declarePrivate('update')
    def update(self, force=False):
        """ Update all harvesters """
        now = datetime.now()
        for item in self.objectValues([ZCatalogHarvester.meta_type]):
            if force or now > item.last_update + timedelta(
                                                days=item.update_interval):
                item.update()
        self.earliestDatestamp()
        super(OAIServer, self).update() #Update repository

    manage_preferences = PageTemplateFile("zpt/manage_OAIServerPrefsForm",
                                          globals())
    security.declareProtected(view_management_screens, 'manage_OAIServerPrefs')
    def manage_OAIServerPrefs(self, REQUEST=None, **kwargs):
        """ manage_preferences """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)
        try:
            process_form(self, IOAIServer, form_data)
        except Exception, e:
            if REQUEST is not None:
                return REQUEST.RESPONSE.redirect(self.absolute_url() +
                    '/manage_main?manage_tabs_message=%s' % quote(str(e)))
            else:
                raise Exception(e)
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_preferences?manage_tabs_message=Settings%20saved')

    security.declareProtected(view_management_screens, 'manage_update')
    def manage_update(self, REQUEST=None):
        """ Manually update all harvesters """
        self.update(True)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=Harvesters%20updated')

    def validate_metadata_prefix(self, metadataPrefix):
        try: #Check if format is ok
            self.get_namespace_dict(metadataPrefix)
        except AttributeError:
            raise CannotDisseminateFormatError

    ################
    # Protocol
    ################

    security.declarePrivate('baseURL')
    def baseURL(self):
        return self.base_url

    security.declarePrivate('repositoryName')
    def repositoryName(self):
        """ """
        return self.repository_name

    security.declarePrivate('protocolVersion')
    def protocolVersion(self):
        """ """
        return self.protocol_version

    security.declarePrivate('adminEmails')
    def adminEmails(self):
        return [x.strip() for x in self.admin_emails.split(',') if x.strip()]

    security.declarePrivate('earliestDatestamp')
    def earliestDatestamp(self):
        """ Last OAIRecord in the repository """
        if getattr(self, 'earliest_datestamp', None):
            return self.earliest_datestamp
        else:
            results = self.getCatalog().searchResults({
                'meta_type': OAIRecord.meta_type,
                'sort_on':'h_datestamp',
                'sort_order':'reverse'
            })
            if len(results) == 0:
                date = datetime.now()
            else:
                date = results[0].h_datestamp
            self.earliest_datestamp = date
            return date

    security.declarePrivate('granularity')
    def granularity(self):
        """ """
        return self.date_granularity

    def get_date(self, date=None):
        """ Return fixed date string depending on granularity of server """
        if date == None:
            zope_date = DateTime.DateTime()
        elif isinstance(date, basestring):
            zope_date = DateTime.DateTime(date)
        elif isinstance(date, datetime):
            zope_date = DateTime.DateTime(str(date))
        else:
            zope_date = date

        granularity = self.granularity()
        if granularity == 'YYYY-MM-DD':
            d_str = str(zope_date.strftime("%Y-%m-%d"))
        elif granularity == 'YYYY-MM-DDThh:mm:ssZ':
            d_str = str(zope_date.HTML4())
        else:
            raise "Unknown granularity: '%s'", granularity
        return d_str

    security.declarePrivate('deletedRecord')
    def deletedRecord(self):
        """ """
        return self.deleted_record

    security.declarePrivate('compression')
    def compression(self):
        """ Not implemented """
        return []

    security.declarePrivate('descriptions')
    def descriptions(self):
        """ Not implemented """
        return []

    security.declarePrivate('identify')
    def identify(self):
        """ Used in pyoai """
        return self

    security.declarePrivate('listMetadataFormats')
    def listMetadataFormats(self, **kw):
        """ Metadata formats from namespace dictionary
        TODO: Fix this when the indexes in the ZCatalog are set right.

        """
        metadata_formats = []
        data_dict = self.get_namespace_dict('oai_dc')
        if kw.has_key('identifier'):
            search_dict = {
                'meta_type': OAIRecord.meta_type,
                'h_identifier': kw['identifier']
            }
            results = self.getCatalog().searchResults(search_dict)
            if len(results) == 0:
                raise IdDoesNotExistError

        metadata_formats.append((data_dict['prefix'], data_dict['schema'],
                                 data_dict['namespace']))
        return metadata_formats

    security.declarePrivate('listSets')
    def listSets(self, **kw):
        """ Not supported """
        raise NoSetHierarchyError

    def _list_records(self, type='listRecords', **kw):
        """ Used in ListRecords and ListIdentifiers because they have similar
        function with the ListIdentifiers having just the header

        Arguments::

            resumptionToken -- A token that allows to iterate OAIRecords
                               (similar to pagination)
            from, until -- Date taken from h_datestamp index in ZCatalog
                    which allows date filtering
            metadataPrefix -- usually oai_dc
            setSpec -- OAI Set filtering (not implemented)

        """
        if 'metadataPrefix' in kw:
            self.validate_metadata_prefix(kw['metadataPrefix'])

        token = None
        offset = 0
        search_dict = {'meta_type': OAIRecord.meta_type}
        search_dict['sort_on'] = 'h_datestamp'
        search_dict['sort_order'] = 'reverse'
        """Get the args for the request either from our 'resumption token' or
        from our regular request dictionary"""
        if 'resumptionToken' in kw:
            #Unserialize the token and populate search_dict
            token = unserialize_token(kw['resumptionToken'])
            if 'metadataPrefix' in token:
                try:
                    self.validate_metadata_prefix(token['metadataPrefix'])
                except CannotDisseminateFormatError:
                    raise BadResumptionTokenError
            offset = int(token.get('offset', 0))
            if 'from' in token and token['from'] != '':
                kw['from_'] = token['from']
            if 'until' in token and token['until'] != '':
                kw['until'] = token['until']

        if 'from_' in kw and 'until' in kw:
            search_dict['h_datestamp'] = {'query': [kw['from_'], kw['until']],
                                          'range': 'minmax'}
        elif 'from_' in kw:
            search_dict['h_datestamp'] = {'query': kw['from_'], 'range': 'min'}
        elif 'until' in kw:
            search_dict['h_datestamp'] = {'query': kw['until'], 'range': 'max'}

        results = self.getCatalog().searchResults(search_dict)

        record_count = 0
        len_results = len(results)
        results_list = [] #OAIRecord list
        resumptionToken = ''
        while (offset + record_count) < len_results:
            # get search record and info
            record = results[offset+record_count]
            header = getattr(record, 'header', "")
            metadata = getattr(record, 'metadata', "")
            about = getattr(record, 'about', "")
            record_count += 1
            if (isinstance(header, Missing) or isinstance(metadata, Missing) or
                isinstance(about, Missing)):
                continue
            if type == 'listRecords':
                results_list.append([header, metadata, about])
            else:
                results_list.append(header)

            if metadata:
                map = metadata._map
                props = ['title', 'description', 'subject', 'type']
                for prop in props:
                    try:
                        if map.has_key(prop) and map[prop][0]:
                            if isinstance(map[prop][0], str) or isinstance(map[prop][0], unicode):
                                map[prop][0] = clean_xml(map[prop][0])
                    except IndexError:
                        continue

                metadata._map = map

            #Create a Token if limit is reached
            if record_count >= self.results_limit:
                new_token = {}
                new_token['offset'] = offset + record_count
                new_token['from'] = ('from_' in kw and
                                     self.get_date(kw['from_']) or '')
                new_token['until'] = ('until' in kw and
                                      self.get_date(kw['until']) or '')
                for key, value in kw.items():
                    if key in token_keys and key not in new_token:
                        new_token[key] = value
                if token is None:
                    resumptionToken = serialize_token(new_token)
                else:
                    token.update(new_token)
                    resumptionToken = serialize_token(token)

                #Not supported in pyoai

                #token_args = {}
                #token_args['cursor'] = offset
                #token_args['completeListSize'] = len_results
                #token_args['expirationDate'] = (DateTime.DateTime() +
                #                    (self.token_expiration/1440.0)).HTML4()
                #token_args['resumptionToken'] = resumptionToken

                break
        return (results_list, resumptionToken)

    security.declarePrivate('listIdentifiers')
    def listIdentifiers(self, **kw):
        """ """
        return self._list_records(type='listIdentifiers', **kw)

    security.declarePrivate('listRecords')
    def listRecords(self, **kw):
        return self._list_records(type='listRecords',**kw)

    security.declarePrivate('getRecord')
    def getRecord(self, **kw):
        if 'identifier' in kw and kw['identifier'] != '':
            record = self.getCatalog().searchResults(
                {'h_identifier': kw.get('identifier')})
            if len(record):
                return [record[0].header, record[0].metadata, u'']
        raise IdDoesNotExistError
