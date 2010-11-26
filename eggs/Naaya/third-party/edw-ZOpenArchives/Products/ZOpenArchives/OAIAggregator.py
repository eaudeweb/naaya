from datetime import datetime, timedelta
from urllib import quote
import pycountry
import os
try:
    import json
except:
    import simplejson as json
try:
    from hashlib import sha1
except:
    from sha import new as sha1

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from Missing import Missing
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, mapper, clear_mappers, aliased
from sqlalchemy.sql import select
import transaction
from zope import interface, schema

from OAIRepository import OAIRepository
from OAIHarvester import OAIHarvester
from OAIRecord import OAIRecord, OAIRecordMapper, OAIRecordMapMapper, \
                                    OAIRecordMapFullMapper
from OAIToken import manage_addOAIToken
import sqlalchemy_setup

from interfaces import IOAIAggregator
from utils import create_object, process_form
from paginator import ObjectPaginator

try:
    import memcache
    memcache_available = True
except ImportError:
    memcache_available = False

manage_addOAIAggregatorForm = PageTemplateFile('zpt/manage_addOAIAggregatorForm',
                                           globals())
def manage_addOAIAggregator(self, id='', REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)
    try:
        ob = create_object(self, OAIAggregator, id)
        process_form(ob, IOAIAggregator, form_data)
        ob.initialize()
    except Exception, e:
        transaction.abort()
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=%s' % quote(str(e)))
        else:
            raise Exception(e)
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/manage_main?update_menu=1')
class OAIAggregator(OAIRepository):
    """ OAI2 Aggregator """
    interface.implements(IOAIAggregator)

    meta_type = 'OAI Aggregator'

    manage_options= (
        {'label': 'Main', 'action': 'manage_main'},
        {'label': 'Preferences', 'action': 'manage_preferences'},
        {'label': 'Update', 'action': 'manage_update'},
    )

    all_meta_types = ({
        'name': OAIHarvester.meta_type,
        'action':
            '/manage_addProduct/ZOpenArchives/manage_addOAIHarvesterForm',
        'product': OAIHarvester.meta_type
        },
    )

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'initialize')
    def initialize(self):
        """ Create what OAIRepository requires. ZCatalog and ZCatalog indexes,
        Create a sqlalchemy storage. It is done here and not in OAIRepository
        because it is uncertain if I need SQLAlchemy in OAIServer.

        """
        super(OAIAggregator, self).initialize()

    security.declarePrivate('add_indexes')
    def add_indexes(self, catalog):
        """ Add indexes for catalog """
        catalog.addIndex('id', 'FieldIndex')
        catalog.addIndex('meta_type', 'FieldIndex')
        catalog.addIndex('harvester', 'FieldIndex')

        catalog.addIndex('dc_author', 'TextIndexNG3')
        catalog.addIndex('dc_contributor', 'KeywordIndex')
        catalog.addIndex('dc_creator', 'KeywordIndex')
        catalog.addIndex('dc_coverage', 'KeywordIndex')
        catalog.addIndex('dc_date', 'KeywordIndex')
        catalog.addIndex('dc_description', 'TextIndexNG3')
        catalog.addIndex('dc_identifier', 'FieldIndex')
        catalog.addIndex('dc_language', 'KeywordIndex')
        catalog.addIndex('dc_title', 'KeywordIndex')
        catalog.addIndex('dc_type', 'KeywordIndex')
        catalog.addIndex('dc_subject', 'KeywordIndex')

    security.declarePrivate('add_metadata')
    def add_metadata(self, catalog):
        """ Adding metadata columns for ZCatalog and SQLAlchemy """
        try:
            catalog.manage_addColumn('id')
        except:
            pass
        try:
            catalog.manage_addColumn('title')
        except:
            pass
        catalog.manage_addColumn('harvester')
        catalog.manage_addColumn('dc_author')
        catalog.manage_addColumn('dc_contributor')
        catalog.manage_addColumn('dc_coverage')
        catalog.manage_addColumn('dc_creator')
        catalog.manage_addColumn('dc_date')
        catalog.manage_addColumn('dc_description')
        catalog.manage_addColumn('dc_identifier')
        catalog.manage_addColumn('dc_language')
        catalog.manage_addColumn('dc_title')
        catalog.manage_addColumn('dc_type')
        catalog.manage_addColumn('dc_subject')

        if self.storage == 'SQLAlchemy': #Fails if no mysql server is installed
            engine = create_engine(self.connection_url)
            sqlalchemy_setup.metadata.drop_all(engine)
            sqlalchemy_setup.metadata.create_all(engine)
            if str(self.connection_url).startswith('mysqldb'):
                engine.execute("ALTER TABLE `records_map_full` ADD FULLTEXT(value)")

    security.declarePrivate('update')
    def update(self):
        """ Update all harvesters """
        now = datetime.now()
        for item in self.objectValues([OAIHarvester.meta_type]):
            if (item.last_update is None or
                now > item.last_update + timedelta(days=item.update_interval)):
                item.update()
        super(OAIAggregator, self).update() #Update repository

    #Example search
    security.declarePublic('search_form')
    search_form = PageTemplateFile('zpt/search_form', globals())

    security.declarePrivate('search_zcatalog')
    def search_sqlalchemy(self, form={}):
        """ Search the OAI Records stored in a sqlite database

        Returns: A list of dictionaries

        """
        session = self.get_session()
        filters = [] #A list of tuples with table to join, join id, and filter
        record_id_column = OAIRecordMapMapper.record_id
        record_map_mapper = [OAIRecordMapMapper, True]
        def get_mapper(mapper):
            """Return an aliased mapper if this is not the first function call
            Used to create joins with the same table

            """
            if mapper[1] is True:
                mapper[1] = False
                return mapper[0]
            else:
                return aliased(mapper[0])

        if form.get('query'):
            record_id_column = OAIRecordMapFullMapper.record_id
            filters.append((OAIRecordMapFullMapper,
                            OAIRecordMapFullMapper.record_id,
                            OAIRecordMapFullMapper.value.match(form['query'])))
        if form.get('identifier'):
            record_id_column = OAIRecordMapper.id
            filters.append((OAIRecordMapper,
                            OAIRecordMapper.id,
                            OAIRecordMapper.id==form['identifier']))
        if form.get('harvester'):
            record_id_column = OAIRecordMapper.id
            filters.append((OAIRecordMapper,
                            OAIRecordMapper.id,
                            OAIRecordMapper.harvester==form['harvester']))
        if form.get('year'):
            table = get_mapper(record_map_mapper)
            filters.append((table,
                            table.record_id,
                            and_(table.key=='dc_date',
                                 table.value==form['year'])))
        if form.get('keywords'):
            table = get_mapper(record_map_mapper)
            filters.append((table,
                            table.record_id,
                            and_(table.key=='dc_subject',
                                 table.value==form['keywords'])))
        if form.get('language'):
            table = get_mapper(record_map_mapper)
            filters.append((table,
                            table.record_id,
                            and_(table.key=='dc_language',
                                 table.value==form['language'])))
        if form.get('coverage'):
            table = get_mapper(record_map_mapper)
            filters.append((table,
                            table.record_id,
                            and_(table.key=='dc_coverage',
                                 table.value==form['coverage'])))
        if form.get('sort_on'):
            order_by = form['sort_on']
        if form.get('sort_order'):
            order_direction = (form['sort_order'] == 'ascending' and 'ascending'
                or 'descending')

        query = session.query(record_id_column)
        joins = []
        first = True
        for table, join_key, _filter in filters: #Appling filters
            query = query.filter(_filter)
            # Do not join with the first table
            if first is True: first = False
            else:
                if table is not None:
                    joins.append((table,
                                  record_id_column==join_key,))

        query = query.join(*joins)
        #How many results (cache if possible)
        records_count = 0
        if memcache_available:
            my_keys = dict(form)

            #Don't create useless hits based on these vars
            if 'per_page' in my_keys:
                del my_keys['per_page']
            if 'page' in my_keys:
                del my_keys['page']

            key = sha1(json.dumps(my_keys)).hexdigest()
            try:
                mc = memcache.Client(['127.0.0.1:11211'], debug=0)
                records_count = mc.get(key)
                if records_count is None:
                    records_count = query.distinct().count()
                    mc.set(key, records_count, 43200)
            except:
                records_count = query.distinct().count()
        else:
            records_count = query.distinct().count()

        limit = int(form.get('per_page', 20))
        offset = limit * int(form.get('page', 0))

        #Fetching record ids with limit and offset
        record_ids = [x[0] for x in
                      query.distinct().limit(limit).offset(offset).all()]

        #Returning maps
        results_list = session.query(
                        OAIRecordMapper.id,
                        OAIRecordMapper.harvester,
                        OAIRecordMapMapper.key,
                        OAIRecordMapMapper.value,
                        OAIRecordMapFullMapper.key,
                        OAIRecordMapFullMapper.value,
                    ).join(OAIRecordMapMapper, OAIRecordMapFullMapper).filter(
                        OAIRecordMapper.id.in_(record_ids)
                    ).all()
        results = []
        for id, harvester, key_map, value_map, key_full, \
            value_full in results_list:
            for row in list(results):
                if row['id'] == id:
                    if key_map:
                        if row.has_key(key_map) and \
                            isinstance(row[key_map], list):
                            if value_map not in results[results.index(row)][key_map]:
                                results[results.index(row)][key_map].\
                                                            append(value_map)
                        else:
                            results[results.index(row)][key_map] = [value_map]

                    if key_full:
                        if row.has_key(key_full) and \
                            isinstance(row[key_full], list):
                            if value_full not in results[results.index(row)][key_full]:
                                results[results.index(row)][key_full].\
                                                            append(value_full)
                        else:
                            results[results.index(row)][key_full] = [value_full]
                    break
            else:
                result_dict = {'id': id, 'harvester': harvester}
                if key_map:
                    result_dict[key_map] = value_map
                if key_full:
                    result_dict[key_full] = value_full
                results.append(result_dict)
        return [results, records_count]

    security.declarePrivate('search_zcatalog')
    def search_zcatalog(self, form={}):
        """ Search the catalog for OAIRecords based on criteria provided by
        form. The brains returned contain all the metadata needed to display
        the result.

        Returns: A list of dictionaries
        """

        or_fields = ('dc_title', 'dc_description', )

        search_dict={'meta_type': OAIRecord.meta_type}
        if form.get('query'): #search all TextIndexNG3 indexes
            search_dict['dc_title'] = form['query']
            search_dict['dc_description'] = form['query']
        if form.get('year'):
            search_dict['dc_date'] = form['year']
        if form.get('language'):
            search_dict['dc_language'] = form['language']
        if form.get('coverage'):
            search_dict['dc_coverage'] = form['coverage']
        if form.get('identifier'):
            search_dict['dc_identifier'] = form['identifier']
        if form.get('harvester'):
            search_dict['harvester'] = form['harvester']
        if form.get('sort_on'):
            search_dict['sort_on'] = form['sort_on']
        if form.get('sort_order'):
            search_dict['sort_order'] = (
                search_dict['sort_order'] == 'ascending' and 'ascending'
                or 'descending')

        if form.get('sort_limit'):
            search_dict['sort_limit'] = int(form['sort_limit'])

        results = []
        if set(or_fields) & set(search_dict.keys()) == set(or_fields):
            search_dict_copy = dict(search_dict)
            for field in or_fields:
                for field in or_fields:
                    try:
                        del(search_dict[field])
                    except KeyError:
                        pass
                search_dict[field] = search_dict_copy[field]
                results.extend(self.getCatalog().searchResults(**search_dict))
        else:
            results = self.getCatalog().searchResults(**search_dict)
        results_list = []
        for result in results: #Create list of dicts from list of brains
            result_dict = {}
            for key, val in self.getCatalog().getMetadataForRID(
                                                result.getRID()).items():
                if not isinstance(val, Missing):
                    result_dict[key] = val
            results_list.append(result_dict)
        return results_list

    security.declarePublic('search')
    def search(self, REQUEST=None, **kw):
        """ Search OAIRecords depending on storage used: SQLAlchemy or ZCatalog

        Returns: ObjectPaginator object

        """
        if REQUEST is not None:
            form = dict(REQUEST.form)
        elif kw:
            form = dict(kw)

        if form == {'-C': ''} or form == {}: #Empty request. No results
            return ObjectPaginator([], 1)

        if self.storage == 'ZCatalog':
            return ObjectPaginator(self.search_zcatalog(form),
                                   int(form.get('per_page', 20)))
        else:
            results = self.search_sqlalchemy(form)
            return ObjectPaginator(results[0],
                                   int(form.get('per_page', 20)), results[1])


    def search_page_link(self, request_dict, page):
        request_dict.update({'page': page})
        return self.absolute_url() + '/search_form?' + '&'.join(
            [('%s=%s' % (quote(str(key)), quote(str(val))))
                for key, val in request_dict.items()])

    security.declarePublic('getOAIAggregators')
    def getOAIAggregators(self):
        """ this should be removed """
        return [self]

    security.declarePublic('get_harvesters')
    def get_harvesters(self):
        """ Getting all harvesters """
        return self.objectValues(OAIHarvester.meta_type)

    security.declarePublic('get_harvesters')
    def get_languages(self):
        """ Search for unique language values """
        languages = []

        if self.storage == 'ZCatalog':
            langs = self.getCatalog().uniqueValuesFor('dc_language')
        else:
            langs = [o.value for o in
                     self.get_session().query(OAIRecordMapMapper.value).\
                     filter(OAIRecordMapMapper.key=='dc_language').\
                     distinct().all()]
        for lang in langs:
            try:
                lang_ob = pycountry.languages.get(
                    alpha2=str(lang).lower())
                languages.append({
                    'name': lang_ob.name,
                    'code': lang_ob.alpha2
                })
            except KeyError:
                continue
        return sorted(languages)

    security.declarePublic('get_language')
    def get_language(self, code):
        """ Get language using ISO-639"""
        try:
            return pycountry.languages.get(alpha2=code).name
        except KeyError:
            return code

    security.declarePrivate('get_session')
    def get_session(self):
        """ Get SQLAlchemy session """
        session = sessionmaker(bind=\
                #create_engine(self.connection_url, echo=True))()
                create_engine(self.connection_url))()
        clear_mappers()
        mapper(OAIRecordMapper, sqlalchemy_setup.tables['records_table'])
        mapper(OAIRecordMapMapper,
               sqlalchemy_setup.tables['records_map_table'])
        mapper(OAIRecordMapFullMapper,
               sqlalchemy_setup.tables['records_map_full_table'])
        return session

    manage_preferences = PageTemplateFile("zpt/manage_OAIAggregatorPrefsForm",
                                          globals())
    security.declareProtected(view_management_screens,
                              'manage_OAIAggregatorPrefs')
    def manage_OAIAggregatorPrefs(self, REQUEST=None, **kwargs):
        """ manage_preferences """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)
        try:
            process_form(self, IOAIAggregator, form_data)
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
        self.update()

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=Harvesters%20updated')

def before_remove_handler(ob, event):
    """ Drop databases """
    pass
