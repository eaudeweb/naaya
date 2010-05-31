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

__doc__ = """ Zope OAI Server """

from DateTime import DateTime
from datetime import datetime, timedelta

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from App.Management import Navigation
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zOAIRepository import zOAIRepository
from ZCatalogHarvester import ZCatalogHarvester

from utils import DT2dt

manage_addZopeOAIServerForm = PageTemplateFile('zpt/manage_addZopeOAIServerForm', globals())

def manage_addZopeOAIServer(self, id='', REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)

    if id == '':
        error = "id field is required"
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST.get('HTTP_REFERER', self.absolute_url() + '/manage_main?') + '&error_message=%s' % quote(error))
        else:
            raise ValueError(error)
    if 'id' in form_data:
        del(form_data['id'])

    OAIO = ZopeOAIServer(id, **form_data)
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')

class ZopeOAIServer(zOAIRepository, Navigation):
    """ """

    meta_type = 'Zope OAI Server'
    all_meta_types = ({'name': ZCatalogHarvester.meta_type, 'action': '/manage_addProduct/edw.ZOpenArchives/manage_addZCatalogHarvesterForm', 'product': ZCatalogHarvester.meta_type}, )
    security = ClassSecurityInfo()

    manage_options = (
        {'label': 'Contents', 'action': 'manage_main'},
        {'label': 'Preferences', 'action': 'manage_preferences' },
        {'label': 'Info', 'action': 'manage_repositoryInfo' },
        {'label': 'Update','action': 'manage_repositoryUpdate'},
    )

    def __init__(self, id='', **kwargs):
        """ """
        self.def_autopublish = kwargs.get('def_autopublish', '1')
        self.def_autopublishRoles = kwargs.get('def_autopublishRoles', [])
        self.namespaces = None
        zOAIRepository.__init__(self, id, kwargs.get('title', 'ZOpen Archives Server'), kwargs.get('def_update_time', '7000'))

    security.declarePrivate('initialize')
    def initialize(self):
        """ """
        zOAIRepository.initialize(self)

    security.declarePrivate('get_namespaceList')
    def get_namespaceList(self, attr='Schema'):
        """
        return list of the named attribute for all namespaces
          either Schema, Shortname, Namespace, Description, Prefix
        """
        nStor = self.get_myNamespaceStorage()
        list = []
        for ns_obj in nStor.objectValues():
            list.append( apply( getattr(ns_obj, 'get_ns' + attr),( )))
        return list

    security.declareProtected(view_management_screens, 'update_repository')
    def update_repository(self, force_update = False):
        """ Get all harvester objects, send update command """
        now = datetime.now()
        for item in self.get_myCatalog().searchResults({'meta_type': ZCatalogHarvester.meta_type}):
            if isinstance(item.last_update, DateTime):
                last_update = DT2dt(item.last_update)
            else:
                last_update = item.last_update

            next_update = last_update + timedelta(minutes=int(item.update_period))
            if force_update or now > next_update:
                zc_harvester = item.getObject()
                zc_harvester.update_ZCatalogHarvester()
        # update timestamp
        self.earliestDatestamp(self.get_earliestDatestamp())
        self.commit_Changes()

        # do stuff of my parent
        ZopeOAIServer.inheritedAttribute('update_repository')(self, force_update=force_update)

    update = update_repository

    security.declarePrivate('add_Indexes')
    def add_Indexes(self, catalog):
        """ Add OAI needed indexes for catalog """
        # general searching - from web form
        catalog.addIndex('OAI_Date', 'FieldIndex')
        catalog.addIndex('OAI_Fulltext', 'TextIndexNG3')
        catalog.addIndex('OAI_Title', 'TextIndexNG3')

        # OAI Search stuff -
        catalog.addIndex('OAI_Identifier', 'FieldIndex')
        catalog.addIndex('OAI_Set', 'KeywordIndex')
        catalog.addIndex('status', 'FieldIndex')
        catalog.addIndex('OAI_MetadataFormat', 'FieldIndex')

        # dc search indexes
        catalog.addIndex('dc_title', 'TextIndexNG3')
        catalog.addIndex('dc_creator', 'KeywordIndex')
        catalog.addIndex('dc_author', 'KeywordIndex')
        catalog.addIndex('dc_subject', 'TextIndexNG3')
        catalog.addIndex('dc_description', 'TextIndexNG3')
        catalog.addIndex('dc_date', 'KeywordIndex')

        # lom search indexes
        # zope searching - in code
        catalog.addIndex('last_update', 'FieldIndex')
        try:
            catalog.addIndex('meta_type', 'FieldIndex')
        except:
            pass
        catalog.addIndex('expiration', 'FieldIndex')

    security.declarePrivate('add_MetadataColumns')
    def add_MetadataColumns(self, catalog):
        """ Add id and title columns if not present """
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

        catalog.manage_addColumn('OAI_Date')
        catalog.manage_addColumn('OAI_Title')
        catalog.manage_addColumn('OAI_Identifier')

        catalog.manage_addColumn('update_period')
        catalog.manage_addColumn('last_update')

        catalog.manage_addColumn('dc_creator')
        catalog.manage_addColumn('dc_author')
        catalog.manage_addColumn('dc_description')
        catalog.manage_addColumn('dc_identifier')

    security.declareProtected(view_management_screens, 'manage_preferences')
    manage_preferences = PageTemplateFile("zpt/manage_ZopeOAIServerPrefsForm", globals())

    security.declareProtected(view_management_screens, 'manage_ZopeOAIServerPrefs')
    def manage_ZopeOAIServerPrefs(self, REQUEST=None, **kwargs):
        """ manage_preferences """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)

        allowed_fields = ('title', 'repositoryName', 'adminEmailList',
            'token_expiration', 'results_limit', 'def_update', 'def_autopublish',
            'def_autopublishRoles', )
        for attr, value in form_data.iteritems():
            if attr in allowed_fields:
                if attr == 'repositoryName':
                    self.repositoryName(value)
                elif attr == 'adminEmailList':
                    self.adminEmail(value)
                else:
                    setattr(self, attr, value)
            else:
                raise ValueError("Unknown field '%s'" % attr)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')
