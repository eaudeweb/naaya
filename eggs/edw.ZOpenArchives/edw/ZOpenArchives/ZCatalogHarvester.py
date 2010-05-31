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

__doc__ = """ Produit ZCatalog Harvester """

import sys
import DateTime
import string
import urllib
import xml.dom.minidom

import App
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from Globals import HTMLFile, Persistent
from OFS.Folder import Folder
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import ZCatalog

from zOAIRecord import manage_addOAIRecord, create_ObjectMetadata

from utils import utConvertLinesToList, utConvertListToLines, processId

manage_addZCatalogHarvesterForm = PageTemplateFile('zpt/manage_addZCatalogHarvesterForm', globals())
def manage_addZCatalogHarvester(self, id="", title="Zope OAI Server", update_period=None, autopublish=1, autopublishRoles = [], pref_meta_types=[], REQUEST=None):
    """ method for adding a new Zope OAI Server """
    if id == '':
        error = "id field is required"
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST.get('HTTP_REFERER', self.absolute_url() + '/manage_main?') + '&error_message=%s' % urllib.quote(error))
        else:
            raise ValueError(error)

    id = 'OAI_' + processId(id)
    pref_meta_types = utConvertLinesToList(pref_meta_types)
    ZCATO = ZCatalogHarvester(id, title, update_period, autopublish, autopublishRoles, pref_meta_types)
    self._setObject(id, ZCATO)
    ZCATO = getattr(self, id)
    ZCATO.initialize()
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')


class ZCatalogHarvester(App.Management.Navigation,BTreeFolder2, Persistent, Implicit):
    """
    name of catalog to index
    """

    meta_type = 'ZCatalog Harvester'
    default_document = 'index_html'

    default_catalog = 'OAI_Catalog'
    default_encoding = 'UTF-8'

    security = ClassSecurityInfo()

    manage_options= (
        {'label': 'Contents', 'action': 'manage_main'},
        {'label': 'Preferences', 'action': 'manage_preferences'},
        {'label': 'Update', 'action': 'manage_update'},
    )

    def __init__(self, id, title, update_period, autopublish, autopublishRoles, pref_meta_types):
        """
        id of harvester is OAI_ + name of catalog
          to index  eg, 'OAI_site_index'
        """
        BTreeFolder2.__init__(self,id)
        self.id = id
        self.title = title
        self.update_period = update_period
        self.last_update = None
        self.autopublish = autopublish
        self.autopublishRoles = filter(None, autopublishRoles)
        self.pref_meta_types = pref_meta_types
        self.force_update = 1
        self.metadata_prefix = None

    security.declarePrivate('initialize')
    def initialize(self):
        """ set generic metadata prefix """
        self.last_update = None
        self.metadata_prefix = 'oai_dc'
        self.allowedRoles = ['Anonymous']
        self.add_oai_index()
        self.update_ZCatalogHarvester()

    security.declareProtected(view_management_screens, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """
        main method for the OAI server. processes
          all incoming URL requests
        get args from request form
        """
        self.the_request = REQUEST.URL0
        return self.process_Request(args=REQUEST.form)

    security.declarePrivate('get_myContainer')
    def get_myContainer(self):
        """ get my parent container """
        # need to do this loop because having problems
        #   getting the real parent - like when adding
        #   a new object to a server
        while (1):
            parent = self.aq_parent
            if parent.id != 'ZOpenArchives':
                break
            self = parent
        return parent

    security.declarePrivate('get_theSiteCatalog')
    def get_theSiteCatalog(self):
        """
        get the catalog in the portail site
        looking for the one with same name as this object
        """
        return self.getSite().getCatalogTool()

    security.declarePrivate('add_oai_index')
    def add_oai_index(self):
        """
        add the oai index to the site catalog
        chosen to publish, index all items
        """
        cat = self.get_theSiteCatalog()
        try:
            cat.addIndex('oai_state', 'FieldIndex')
            cat.manage_reindexIndex(ids='oai_state')
        except:
            pass

    security.declarePrivate('delete_oai_index')
    def delete_oai_index(self):
        """delete the index from the site catalog chosen to publish"""
        cat = self.get_theSiteCatalog()
        cat.delIndex('oai_state')

    security.declarePrivate('update_ZCatalogHarvester')
    def update_ZCatalogHarvester(self):
        """get cataloged objects, set update time, re-index"""
        self.last_update = DateTime.DateTime()
        self.update_CatalogItems()
        self.reindex_object()

    security.declarePrivate('update_CatalogItems')
    def update_CatalogItems(self):
        """ update get all items in catalog """
        # always do manual publish - in case someone adds other
        #   information that they want shared, other than what
        #   autopublish provides
        #self.process_Manualpublish()
        if self.autopublish == "1":
            self.process_Autopublish()
        else:
            self.process_Manualpublish()
        # now look for objects which have been deleted in the portal catalog
        #TOSEE - self.process_deletedObjects()

    security.declarePrivate('delete_Records')
    def delete_Records(self):
        """ sometimes it's necessary to clean out the records """
        self.manage_delObjects( ids = self.objectIds('Open Archive Record') )

    security.declarePrivate('process_Autopublish')
    def process_Autopublish(self):
        """method to process all objects in the Portal catalog just uses Dublin Core """
        if self.pref_meta_types is not None and self.pref_meta_types != []:
            searchDict = {'meta_type': self.pref_meta_types}
        else:
            searchDict = {'oai_state':'shared'}
        for item in ZCatalog.searchResults( self.get_theSiteCatalog(), searchDict ):
            # get object and create its metadata structure, check to make sure that the object still exists
            #   not just the reference in the catalog
            try:
                obj = item.getObject()
            except:
                obj=None
            if obj == None:
                print "Error process_Autopublish: referenced object not found in catalog", item.id
                continue
            # see if the harvester already has the object
            #   decide whether to update or add new one
            path = urllib.unquote( '/' + obj.absolute_url(1) + '-oai_dc'  )
            pid = processId(path)
            OAIO = self._getOb( pid, None)

            # check to see if we need to update the object, either
            #   - it has been updated since last time force update is specified
            #   - if it is a new object
            update = 0
            if self.last_update.greaterThan(obj.bobobase_modification_time()):
                update = 1
            if self.force_update == 1:
                update = 1
            if OAIO == None:
                update = 1

            if update == 0:
                # we don't create new XML, but we still have
                #   to call the update to the zOAIRecord so
                #   that it doesn't get marked as 'deleted'
                #   None signals object is still there, but not changed
                record_xml = None
            else:
                # get all namespaces for this object
                # they are used for searching the XML tags
                ns_dict = self.get_myContainer().get_namespaceInfoByPrefix('oai_dc')

                # create dictionary for object information
                #  to pass it into create_ObjectMetadata()
                # TODO : use get_MetadataDictionary in metadataaware
                obj_data = {}
                obj_data['header_tags'] = h_tags = {}
                obj_data['metadata_tags'] = m_tags = {}

                site_domain = self.get_myContainer().repositoryDomain()
                id =  'oai:'+ site_domain + ':' + '/' + obj.absolute_url(1)
                h_tags['identifier'] = urllib.unquote(id)
                h_tags['datestamp'] = self.get_myContainer().get_fixedDate(str(obj.bobobase_modification_time()))

                m_tags['dc:identifier'] = obj.absolute_url()
                if hasattr(obj, 'Title'):
                    title = obj.Title()
                else:
                    title = obj.title_or_id()
                m_tags['dc:title'] = title
                if hasattr(obj, 'description'):
                    description = obj.description
                else:
                    description = 'n/a'
                m_tags['dc:description'] = description
                if hasattr(obj, 'subject'):
                    subject = obj.keywords
                else:
                    subject = 'n/a'
                m_tags['dc:subject'] = subject
                if hasattr(obj, 'Type'):
                    type = obj.Type()
                else:
                    type = obj.meta_type
                m_tags['dc:type'] = type
                m_tags['dc:date'] = self.get_myContainer().get_fixedDate(str(obj.bobobase_modification_time()))
                if hasattr(obj, 'contributor'):
                    creator = obj.contributor
                else:
                    for user, roles in obj.get_local_roles():
                        if 'Owner' in roles:
                            creator = user
                            break
                m_tags['dc:creator'] = creator
                # get object's metadata XML formattted to OAI specs
                record_xml = create_ObjectMetadata(obj, obj_data, ns_dict=ns_dict,
                                                   type='xml', def_enc=self.default_encoding)
            if OAIO != None:
                OAIO.update_Record(xml=record_xml)
            else:
                manage_addOAIRecord(self, metadata_format='oai_dc', id=pid, xml=record_xml)
        self.force_update = 0

    security.declarePrivate('process_Manualpublish')
    def process_Manualpublish(self):
        """
        need to create different types of objects depending
        on the various types of metadata associated with
        the original object - this is for the cataloging
        and quick serving of information
        """
        if self.pref_meta_types is not None and self.pref_meta_types != []:
            searchDict = {'meta_type': self.pref_meta_types}
        else:
            searchDict = {'oai_state':'shared'}
        # override portal_catalog searchResults, use directly
        #   that of ZCatalog
        for item in ZCatalog.searchResults( self.get_theSiteCatalog(), searchDict ):
            # get object and create its metadata structure
            #   check to make sure that the object still exists
            #   not just the reference in the catalog
            obj = item.getObject()
            if obj == None:
                print "Error: not found in process_Manualpublish", item.id
                continue

            available_metadata = obj.get_metadataTypes()

            for metadata in available_metadata:
                # take each one, check if exists see if the harvester already has the object
                #   decide whether to update or add new one
                path = urllib.unquote( '/' + obj.absolute_url(1) + '-' + metadata )
                pid = processId(path)
                OAIO = self._getOb( pid, None)
                # check to see if we need to update the object
                #   - been updated since last time
                #   - need to force update
                #   - if the object is new
                #
                update = 0
                if self.last_update.greaterThan(obj.bobobase_modification_time()):
                    update = 1
                if self.force_update == 1:
                    update = 1
                if OAIO == None:
                    update = 1

                if update == 0:
                    # we don't create new XML, but we still have
                    #   to call the update to the zOAIRecord so
                    #   that it doesn't get marked as 'deleted'
                    record_xml = None
                else:
                    # get all namespaces for this object
                    # they are used for searching the XML tags
                    #
                    # get xml and create dom
                    # TODO: capture error
                    record_dom = obj.get_metadataDOM(prefix=metadata)
                    # record_dom = xml.dom.minidom.parseString(record_xml)
                    from_meta_node = record_dom
                    xmldoc = xml.dom.minidom.Document()
                    # xmldoc.createProcessingInstruction('xml', 'version="1.0" encoding="%s"' % self.default_encoding )

                    # create <record> node
                    n_record = xmldoc.createElement("record")
                    xmldoc.appendChild(n_record)

                    # ###############
                    # add <header>
                    #
                    n_header = xmldoc.createElement("header")
                    n_record.childNodes.append(n_header)

                    # add child <identifier>
                    h_id = xmldoc.createElement('identifier')
                    n_header.appendChild(h_id)

                    # TODO: put oai name in attribute
                    site_domain = self.get_myContainer().repositoryDomain()
                    id =  'oai:'+ site_domain + ':' + '/' + obj.absolute_url(1)
                    id = urllib.unquote(id)
                    h_id.appendChild(xmldoc.createTextNode(id))

                    h_date = xmldoc.createElement('datestamp')
                    n_header.appendChild(h_date)

                    date = self.get_myContainer().get_fixedDate(str(obj.bobobase_modification_time()))
                    h_date.appendChild(xmldoc.createTextNode(date))


                    # ####################
                    # add <metadata> tag
                    #
                    n_metadata = xmldoc.createElement("metadata")
                    n_record.childNodes.append(n_metadata)
                    to_meta_node = n_metadata

                    c2 = from_meta_node.cloneNode(1)
                    to_meta_node.appendChild(c2)

                    record_xml =  xmldoc.toxml(self.default_encoding)

                if OAIO != None:
                    OAIO.update_Record(xml=record_xml)
                else:
                    manage_addOAIRecord(self, metadata_format=metadata, id=pid, xml=record_xml)
        self.force_update = 0

    security.declarePrivate('process_deletedObjects')
    def process_deletedObjects(self):
        """ """
        # look for items not updated, and mark as deleted
        catalog = getattr( self.get_myContainer(), self.default_catalog )
        for item in catalog.searchResults( {'last_update':self.last_update,
                                            'last_update_usage':'range:max',
                                            'status':'available'} ):
            record = item.getObject()
            if record == None:
                continue
            # TODO: deleted record support - yes, no, transient
            record.mark_recordDeleted()

    security.declarePrivate('index_object')
    def index_object(self):
        """ """
        try:
            getattr(self, self.default_catalog).catalog_object(self, urllib.unquote('/' + self.absolute_url(1) ))
        except:
            pass

    security.declarePrivate('unindex_object')
    def unindex_object(self):
        """ """
        try:
            getattr(self, self.default_catalog).uncatalog_object(urllib.unquote('/' + self.absolute_url(1) ))
        except:
            pass

    security.declarePrivate('reindex_object')
    def reindex_object(self):
        """ """
        self.unindex_object()
        self.index_object()

    ###################
    # ZMI Views
    ###################

    security.declareProtected(view_management_screens, 'manage_preferences')
    manage_preferences = PageTemplateFile("zpt/manage_ZCatalogHarvesterPrefsForm", globals())

    security.declareProtected(view_management_screens, 'manage_ZCatalogHarvesterPrefs')
    def manage_ZCatalogHarvesterPrefs(self, title, update_period, autopublish, autopublishRoles=[], pref_meta_types=[], REQUEST=None):
        """ save preferences """
        self.title = title
        if self.autopublish != autopublish:
            self.autopublish = autopublish
            self.delete_Records()
        self.autopublishRoles = filter(None, autopublishRoles)
        self.pref_meta_types = filter(None, pref_meta_types)
        self.update_period = update_period
        self.force_update = 1
        self.reindex_object() # need to recatalog update_period
        self.update_ZCatalogHarvester()
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')


    security.declareProtected(view_management_screens, 'manage_update')
    manage_update = HTMLFile("dtml/manage_ZCatalogHarvesterUpdateForm", globals())

    security.declareProtected(view_management_screens, 'manage_ZCatalogHarvesterUpdate')
    def manage_ZCatalogHarvesterUpdate(self, REQUEST=None):
        """ update catalog records """
        self.update_ZCatalogHarvester()
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Site%20records%20updated')

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        """ XXX: This method is deprecated """
        # self.delete_oai_index()
        self.unindex_object()
        BTreeFolder.inheritedAttribute("manage_beforeDelete")(self, item, container)
