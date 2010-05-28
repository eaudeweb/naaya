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

__doc__ = """ Zope OAI Aggregator """

from urllib import quote

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zOAIRepository import zOAIRepository
from zOAIHarvester import zOAIHarvester

manage_addOAIAggregatorForm = PageTemplateFile('zpt/manage_addOAIAggregatorForm', globals())

def manage_addOAIAggregator(self, id='', title="OAI Aggregator", minutes=18000, REQUEST=None):
    """ """
    if id == '':
        error = "id field is required"
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST.get('HTTP_REFERER', self.absolute_url() + '/manage_main?') + '&error_message=%s' % quote(error))
        else:
            raise ValueError(error)

    OAIO = zOAIAggregator(id, title, minutes)
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?updat_menu=1')

class zOAIAggregator(zOAIRepository):
    """ This is the container that stores the fetched data from OAI servers """

    meta_type = 'Open Archive Aggregator'

    security = ClassSecurityInfo()

    all_meta_types = ({'name': zOAIHarvester.meta_type, 'action': '/manage_addProduct/edw.ZOpenArchives/manage_addOAIHarvesterForm', 'product': zOAIHarvester.meta_type}, )


    security.declarePrivate('add_Indexes')
    def add_Indexes(self, catalog):
        """ """
        catalog.addIndex('OAI_Date', 'FieldIndex')
        catalog.addIndex('OAI_Fulltext', 'TextIndexNG3')
        catalog.addIndex('OAI_Title', 'TextIndexNG3')
        catalog.addIndex('dc_creator', 'TextIndexNG3')
        catalog.addIndex('dc_author', 'TextIndexNG3')
        catalog.addIndex('dc_description', 'TextIndexNG3')
        catalog.addIndex('dc_type', 'TextIndexNG3')
        catalog.addIndex('meta_type', 'FieldIndex')

        #OAI Search
        catalog.addIndex('OAI_Identifier', 'FieldIndex')
        catalog.addIndex('OAI_Set', 'KeywordIndex')
        catalog.addIndex('expiration', 'FieldIndex')

    security.declarePrivate('add_Indexes')
    def add_MetadataColumns(self, catalog):
        """ """
        try:
            catalog.manage_addColumn('id')
        except:
            pass
        try:
            catalog.manage_addColumn('title')
        except:
            pass
        catalog.manage_addColumn('header')
        catalog.manage_addColumn('metadata')
        catalog.manage_addColumn('OAI_Date')
        catalog.manage_addColumn('OAI_Title')
        catalog.manage_addColumn('OAI_Identifier')
        catalog.manage_addColumn('dc_creator')
        catalog.manage_addColumn('dc_author')
        catalog.manage_addColumn('dc_type')
        catalog.manage_addColumn('dc_identifier')
        catalog.manage_addColumn('dc_description')

    security.declarePrivate('getHarvesters')
    def getHarvesters(self):
        """ """
        harvesters_list =[]
        harvesters = self.objectItems('Open Archive Harvester')
        for i in range(len(harvesters)):
            harvesters_list.append(harvesters[i][1])
        return harvesters_list

    security.declareProtected(view_management_screens, 'manage_preferences')
    manage_preferences = PageTemplateFile("zpt/manage_OAIAggregatorPrefsForm",globals())

    security.declareProtected(view_management_screens, 'manage_OAIRepositoryPrefs')
    def manage_OAIRepositoryPrefs(self, title, def_update, token_expiration, results_limit, REQUEST=None, RESPONSE=None):
        """ save preferences """
        self.title = title
        self.def_update = def_update
        self.token_expiration = token_expiration
        self.results_limit = results_limit
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')
