import logging
import re
from datetime import datetime
from oaipmh.common import Header, Metadata
from urllib import quote

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from App.Management import Navigation
from Globals import Persistent
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from zope import interface

from OAIRecord import OAIRecord, manage_addOAIRecord
from interfaces import IZCatalogHarvester
from utils import processId, create_object, process_form, DT2dt, \
                utConvertLinesToList, clean_xml

manage_addZCatalogHarvesterForm = PageTemplateFile(
                            'zpt/manage_addZCatalogHarvesterForm', globals())
def manage_addZCatalogHarvester(self, id="", REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)
    try:
        if id == '':
            id = processId(form_data.get('title', 'zharvester')).lower()
        form_data['search_meta_types'] = utConvertLinesToList(
            form_data.get('search_meta_types',''))
        ob = create_object(self, ZCatalogHarvester, id)
        process_form(ob, IZCatalogHarvester, form_data)
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

class ZCatalogHarvester(BTreeFolder2, Persistent, Implicit):
    """ """
    interface.implements(IZCatalogHarvester)

    meta_type = 'ZCatalog Harvester'

    security = ClassSecurityInfo()

    manage_options= (
        {'label': 'Main', 'action': 'manage_main'},
        {'label': 'Preferences', 'action': 'manage_preferences'},
        {'label': 'Update', 'action': 'manage_update'},
    )


    all_meta_types = ({
        'name': OAIRecord.meta_type,
        'action':
            '/manage_addProduct/ZOpenArchives/manage_addZCatalogHarvesterForm',
        'product': OAIRecord.meta_type
        },
    )

    security.declarePrivate('initialize')
    def initialize(self):
        """ """
        self.update()

    security.declarePrivate('update')
    def update(self, force=False):
        """This updates the data from the ZCatalog. Essensially searching the
        meta_types in the portal catalog and mapping them to OAIRecord's

        """
        if self.search_meta_types:
            search_dict = {'meta_type': self.search_meta_types}
        else:
            search_dict = {'oai_state': 'shared'}

        ns_dict = self.aq_parent.get_namespace_dict('oai_dc')
        visited_records = []
        results = ZCatalog.searchResults(self.get_site_catalog(), search_dict)

        for item in results: #Creating/updating OAIRecords
            try:
                ob = item.getObject()
            except:
                logging.info('Could not find the object from catalog')
                continue

            # check if the harvester already has the object
            path = '/'.join(ob.getPhysicalPath()) + '-oai_dc'
            record_id = processId(path)
            oai_record = self._getOb(record_id, None)
            visited_records.append(record_id)

            #Needs to be updated?
            if (force is True or oai_record is None or self.last_update is None
                or self.last_update > DT2dt(ob.bobobase_modification_time())):
                #Construct OAIRecord
                ob_data = {}

                #Header of the record
                id = 'oai:%s%s' % (processId(self.aq_parent.repositoryName()).lower(),
                                    ':'.join(ob.getPhysicalPath()).lower())
                ob_data['OAI_Identifier'] = id
                header = Header(id, DT2dt(ob.bobobase_modification_time()),
                                           [], False)

                #Setting up metadata of the record
                m_tags = {}
                m_tags['identifier'] = [ob.absolute_url()]
                m_tags['OAI_Identifier'] = id

                if hasattr(ob, 'Title'):
                    title = ob.Title()
                else:
                    title = ob.title_or_id()
                m_tags['title'] = [clean_xml(title)]

                if hasattr(ob, 'description') and ob.description:
                    description = re.sub(r'<[^>]*?>', '', ob.description)
                else:
                    description = 'n/a'
                m_tags['description'] = [clean_xml(description)]

                if hasattr(ob, 'keywords') and ob.keywords:
                    if getattr(ob.keywords, '__iter__', False):
                        m_tags['subject'] = clean_xml(ob.keywords)
                    elif ',' in ob.coverage:
                        m_tags['subject'] = [clean_xml(x.strip()) for x in
                                    ob.keywords.split(',') if x.strip() != '']
                    else:
                        m_tags['subject'] = [clean_xml(ob.keywords)]
                else:
                    m_tags['subject'] = ['n/a']

                if hasattr(ob, 'Type'):
                    type = ob.Type()
                else:
                    type = ob.meta_type

                m_tags['type'] = [clean_xml(type)]
                m_tags['date'] = [self.aq_parent.get_date(
                    ob.bobobase_modification_time())]

                if hasattr(ob, 'contributor'):
                    creator = ob.contributor
                else:
                    for user, roles in ob.get_local_roles():
                        if 'Owner' in roles:
                            creator = user
                            break
                m_tags['creator'] = [creator]

                if hasattr(ob, 'coverage') and ob.coverage:
                    if getattr(ob.coverage, '__iter__', False):
                        m_tags['coverage'] = ob.coverage
                    elif ',' in ob.coverage:
                        m_tags['coverage'] = [ x.strip() for x in
                                    ob.coverage.split(',') if x.strip() != '']
                    else:
                        m_tags['coverage'] = [ob.coverage]

                metadata = Metadata(m_tags)

                if oai_record:
                    oai_record.update(**ob_data)
                else:
                    manage_addOAIRecord(self, id=record_id, **ob_data)
                    oai_record = self._getOb(record_id)

                #Updating header and metadata
                oai_record.header = header
                oai_record.metadata = metadata
                oai_record.reindex_object()
                self.last_update = datetime.now()

        #Deleting unaffected OAIRecords - it means that they where not in
        #sites ZCatalog when updating
        for oai_record in self.getCatalog().searchResults(
            meta_type=OAIRecord.meta_type, harvester=self.id):
            if oai_record.id not in visited_records:
                try:
                    self.manage_delObjects(oai_record.id)
                except:
                    continue

    security.declarePrivate('clear')
    def clear(self):
        """Delete all OAIRecord items the container """
        self.manage_delObjects([OAIRecord.meta_type, ])

    security.declarePrivate('update')
    def get_site_catalog(self):
        """Try to get portal's catalog"""
        try: #This is from Naaya
            return self.getSite().getCatalogTool()
        except AttributeError: #Test case
            return self.aq_parent.aq_parent._getOb('catalog')
        else:
            raise AttributeError('Missing site ZCatalog')

    manage_preferences = PageTemplateFile(
        "zpt/manage_ZCatalogHarvesterPrefsForm", globals())

    security.declareProtected(view_management_screens,
                              'manage_ZCatalogHarvesterPrefs')
    def manage_ZCatalogHarvesterPrefs(self, REQUEST=None, **kwargs):
        """ manage_preferences """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)
        form_data['search_meta_types'] = utConvertLinesToList(
            form_data.get('search_meta_types',''))
        try:
            autopublish = self.autopublish
            process_form(self, IZCatalogHarvester, form_data)

            if self.autopublish != autopublish:
                self.clear()
            self.update()

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
        self.update(True)
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=Site%20records%20updated')
