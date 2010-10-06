from datetime import datetime
import logging
from urllib import quote
from oaipmh import client, metadata
from oaipmh.error import XMLSyntaxError, XMLValidationError
import pycountry

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from App.Management import Navigation
import DateTime
from Globals import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
import transaction

from zope import interface, schema

import sqlalchemy_setup
from OAIRecord import OAIRecord, OAIRecordMapper, OAIRecordMapMapper, \
                        OAIRecordMapFullMapper, manage_addOAIRecord
from OAIToken import manage_addOAIToken
from interfaces import IOAIHarvester
from utils import create_object, process_form, processId, url_pattern, \
                                                                ListDictDiffer

manage_addOAIHarvesterForm = PageTemplateFile('zpt/manage_addOAIHarvesterForm',
                                              globals())
def manage_addOAIHarvester(self, id='', REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)
    try:
        if id == '':
            id = processId(form_data.get('title', 'zharvester')).lower()
        ob = create_object(self, OAIHarvester, id)
        process_form(ob, IOAIHarvester, form_data)
        ob.update_sets()
    except Exception, e:
        transaction.abort()
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=%s' % quote(str(e)))
        else:
            raise
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/manage_main?update_menu=1')

class OAIHarvester(BTreeFolder2, Persistent, Implicit):
    """ This harvester collects data from remote sources """
    interface.implements(IOAIHarvester)

    meta_type = 'OAI Harvester'

    manage_options= (
        {'label': 'Main', 'action': 'manage_main'},
        {'label': 'Preferences', 'action': 'manage_preferences'},
        {'label': 'Update', 'action': 'manage_update'},
    )

    security = ClassSecurityInfo()

    def get_connection(self):
        """ Establish connection with the OAI Server """
        metadata_registry = metadata.MetadataRegistry(flags=['xml:lang'])
        #Registering a reader that will return the fields in this form:
        #dc_field:lang_code
        metadata_registry.registerReader('oai_dc', metadata.oai_dc_reader)

        if self.username and self.password:
            return client.Client(self.url, metadata_registry,
                                (self.username, self.password, ))
        else:
            return client.Client(self.url, metadata_registry)

    security.declarePrivate('update_zcatalog')
    def update_zcatalog(self, records_reponse):
        """ Fetch data from an OAI Server and populate the repository's catalog
        Highly inneficient in terms of storage. It is not recommended to use
        ZCatalog storage.

        Arguments:
        records_reponse -- <record> Generator

        """
        visited_records = []
        catalog = self.aq_parent.getCatalog()
        for (header, meta, about), token in records_reponse:
            if not header or not meta: #Invalid record, passing through
                continue

            id = processId(header.identifier())
            catalog_record = catalog.searchResults(
                meta_type=OAIRecord.meta_type, id=id)
            visited_records.append(id)

            if len(catalog_record):
                record = catalog_record[0].getObject()
            else:
                manage_addOAIRecord(self, id=id, deleted=header.isDeleted(),
                                    about=unicode(about))
                record = self._getOb(id)
                record.harvester = self.id

            #Storing some fields for ZCatalog
            for key, val in meta.getMap().iteritems():
                if key == 'identifier' and val:
                    for ident in val:
                        if url_pattern.match(ident): #Storing only the url
                            record.dc_identifier = ident
                            break
                    else:
                        record.dc_identifier = val[0]
                elif key == 'description' and val:
                    record.dc_description = "\n".join(val)
                elif key == 'type' and val:
                    record.dc_type = "\n".join(val)
                elif key == 'author' and val:
                    record.dc_author = "\n".join(val)
                elif key == 'language' and val:
                    record.dc_language = []
                    for lang in val:
                        try:
                            record.dc_language.append(
                                pycountry.languages.get(
                                    alpha2=str(lang).lower()
                                ).alpha2
                            )
                        except KeyError:
                            continue
                else:
                    setattr(record, 'dc_' + key, val)

            record.header = header
            record.metadata = meta
            record.reindex_object()

            if self.resume_token != token:
                self.resume_token = token
                try:
                    transaction.commit()
                except:
                    pass

        #Deleting unaffected OAIRecords
        for oai_record in self.getCatalog().searchResults(
            meta_type=OAIRecord.meta_type, harvester=self.id):
            if oai_record.id not in visited_records:
                self.manage_delObjects(oai_record.id)


    security.declarePrivate('update_sqlalchemy')
    def update_sqlalchemy(self, records_reponse):
        """ The recommended way to store OAI Records from remote servers

        Arguments:
        records_reponse -- <record> Generator

        """
        session = self.aq_parent.get_session()
        record_insert_list = []

        record_map_insert_list = []
        record_full_insert_list = []

        record_map_delete_list = []
        record_full_delete_list = []

        try:
            for (header, meta, about), token in records_reponse:
                if not header or not meta: #Invalid record, passing through
                    continue
                record_id = processId(header.identifier())
                record = session.query(OAIRecordMapper).filter(
                    OAIRecordMapper.id==record_id).all()

                record_map = []
                if record:
                    record = record[0]
                    if header.isDeleted():
                        session.delete(record)
                        session.commit()
                        continue
                    #Get existing records
                    record_maps = session.query(OAIRecordMapMapper).\
                    filter(OAIRecordMapMapper.record_id==record_id).all()

                    record_fullmaps = session.query(OAIRecordMapFullMapper).\
                    filter(OAIRecordMapFullMapper.record_id==record_id).all()

                    for map_item in record_maps:
                        record_map.append({
                            'id': map_item.id,
                            'lang': map_item.lang,
                            'record_id': map_item.record_id,
                            'key': map_item.key,
                            'value': map_item.value
                        })

                    for map_item in record_fullmaps:
                        record_map.append({
                            'id': map_item.id,
                            'lang': map_item.lang,
                            'record_id': map_item.record_id,
                            'key': map_item.key,
                            'value': map_item.value
                        })
                else:
                    record_insert_list.append({'id': record_id,
                                                'harvester': self.id})
                new_record_map = []
                #Get the request metadata data dict and make it flat
                for key, values in meta.getMap().iteritems():
                    if key.find(':') != -1:
                        key, lang = key.split(':')
                    else:
                        lang = None

                    map_dict = {
                        'record_id': record_id,
                        'lang': lang,
                        'key': unicode('dc_' + key),
                    }
                    for value in values:
                        if value:
                            if key == 'identifier':
                                #Storing only the url
                                if url_pattern.match(value):
                                    map_dict.update({'value': value})
                                    new_record_map.append(dict(map_dict))
                                    break
                            elif key == 'language':
                                try:
                                    country_code = pycountry.languages.get(
                                        alpha2=str(value).lower()
                                    ).alpha2
                                    map_dict.update({'value': country_code})
                                    new_record_map.append(dict(map_dict))
                                except:
                                    continue
                            else:
                                map_dict.update({'value': value})
                                new_record_map.append(dict(map_dict))

                diff = ListDictDiffer(new_record_map, record_map, ('id', ))

                #Insert list
                for map_dict in diff.added():
                    if map_dict['key'] in ('dc_title', 'dc_description'):
                        record_full_insert_list.append(map_dict)
                    else:
                        record_map_insert_list.append(map_dict)

                #Delete list - write some tests for this
                for list_index in diff.removed_index():
                    map_dict = record_map[list_index]
                    if map_dict['key'] in ('dc_title', 'dc_description'):
                        record_full_delete_list.append(map_dict['id'])
                    else:
                        record_map_delete_list.append(map_dict['id'])

                #Resumption token changed -> Make a bulk insert/delete
                if self.resume_token != token:
                    self.resume_token = token
                    try:
                        transaction.commit()
                    except:
                        pass

                    if record_insert_list:
                        session.bind.execute(
                            sqlalchemy_setup.tables['records_table'].\
                            insert(),
                            record_insert_list)
                        record_insert_list = []

                    #Insert
                    if record_map_insert_list:
                        session.bind.execute(
                            sqlalchemy_setup.tables['records_map_table'].\
                            insert(),
                            record_map_insert_list)
                        record_map_insert_list = []

                    if record_full_insert_list:
                        session.bind.execute(
                            sqlalchemy_setup.tables['records_map_full_table'].\
                            insert(),
                            record_full_insert_list)
                        record_full_insert_list = []

                    if record_map_delete_list:
                        table = sqlalchemy_setup.tables['records_map_table']
                        session.bind.execute(
                            table.delete().where(
                                table.columns.id.in_(record_map_delete_list))
                        )
                        record_map_delete_list = []

                    if record_full_delete_list:
                        table = sqlalchemy_setup.tables['records_map_full_table']
                        session.bind.execute(
                            table.delete().where(
                                table.columns.id.in_(record_full_delete_list))
                        )
                        record_full_delete_list = []

        except XMLSyntaxError, e:
            logging.error('Update failed with: %s' % str(e))
        except XMLValidationError:
            logging.error('Update failed due to an XMLValidation error')

    security.declarePrivate('update_sets')
    def update_sets(self):
        """ Updating list of sets

        Arguments:

        """
        con = self.get_connection()
        self.list_sets = []
        try:
            for set_item in con.listSets():
                self.list_sets.append({'spec': str(set_item[0]),
                                   'name': unicode(set_item[1])})
        except:
            try: self.getSite().log_current_error()
            except: pass

    security.declarePrivate('update')
    def update(self):
        """ Update depending on storage type """
        con = self.get_connection()

        #Filter results by setSpec
        if not self.list_sets_all and self.list_sets_selected:
            records_reponse = []
            for spec in self.list_sets_selected:
                if self.resume_token:
                    try:
                        records_reponse = con.listRecords(
                                            metadataPrefix='oai_dc',
                                            resumptionToken=self.resume_token,
                                            setSpec=spec)
                    except XMLValidationError, e:
                        logging.error('XMLValidation Error: %r' % str(e))
                        return
                else:
                    records_reponse = con.listRecords(metadataPrefix='oai_dc',
                                                           setSpec=spec)
                if self.aq_parent.storage == 'ZCatalog':
                    self.update_zcatalog(records_reponse)
                else:
                    self.update_sqlalchemy(records_reponse)
        else:
            #User resume token if update has been stoped in the middle
            try:
                if self.resume_token:
                    records_reponse = con.listRecords(metadataPrefix='oai_dc',
                                            resumptionToken=self.resume_token)
                else:
                    records_reponse = con.listRecords(metadataPrefix='oai_dc')
            except XMLValidationError, e:
                logging.error('XMLValidation Error: %r' % str(e))
                return

            if self.aq_parent.storage == 'ZCatalog':
                self.update_zcatalog(records_reponse)
            else:
                self.update_sqlalchemy(records_reponse)

        #Updating list sets
        self.update_sets()

        self.last_update = datetime.now()
        self.resume_token = u''

    def records(self, limit=10, order_by='date_added'):
        """ Getting a list of tuples of OAIRecords for the current harvester
        depending on storage type

        """
        records = []
        if self.aq_parent.storage == 'ZCatalog':
            for oai_record in self.objectValues(OAIRecord.meta_type)[:limit]:
                records.append((oai_record.metadata['identifier'][0],
                                oai_record.metadata['title'][0]))
        else:
            session = self.aq_parent.get_session()
            oai_records = session.query(OAIRecordMapper).\
            filter(OAIRecordMapper.harvester==self.id).\
            order_by(order_by)[:limit]
            oai_record_ids = [x.id for x in oai_records]
            oai_records_map = dict(session.query(
                OAIRecordMapMapper.record_id, OAIRecordMapMapper.value).\
                filter(OAIRecordMapMapper.record_id.in_(oai_record_ids)).\
                filter(OAIRecordMapMapper.key == 'dc_identifier').all())
            oai_records_full = dict(session.query(
                OAIRecordMapFullMapper.record_id, OAIRecordMapFullMapper.value).\
                filter(OAIRecordMapFullMapper.record_id.in_(oai_record_ids)).\
                filter(OAIRecordMapFullMapper.key == 'dc_title').all())
            for oai_record_id in oai_record_ids:
                if (oai_records_map.has_key(oai_record_id) and
                    oai_records_full.has_key(oai_record_id)):
                    records.append((oai_records_map[oai_record_id],
                                oai_records_full[oai_record_id]))
        return records

    security.declareProtected(view_management_screens, 'manage_preferences')
    manage_preferences = PageTemplateFile("zpt/manage_OAIHarvesterPrefsForm",
                                          globals())

    security.declareProtected(view_management_screens,
                              'manage_OAIHarvesterPrefs')
    def manage_OAIHarvesterPrefs(self, REQUEST=None, **kwargs):
        """ manage_preferences """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)
        list_sets_selected = form_data.get('list_sets_selected')
        if list_sets_selected and isinstance(list_sets_selected,
                                             (str, unicode)):
            form_data['list_sets_selected'] = [list_sets_selected]
        try:
            process_form(self, IOAIHarvester, form_data)
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
        """ update catalog records """
        self.update()
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=Site%20records%20updated')
