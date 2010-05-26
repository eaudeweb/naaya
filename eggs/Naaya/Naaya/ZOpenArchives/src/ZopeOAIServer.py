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


from Globals import HTMLFile
from AccessControl import ClassSecurityInfo
import DateTime
from zOAIRepository import zOAIRepository
import zOAINamespace
from pyOAIMH.OAINamespace import oai_dc_defaults
import App
from utils import utConvertLinesToList

manage_addZopeOAIServerForm = HTMLFile('dtml/manage_addZopeOAIServerForm', globals())

def manage_addZopeOAIServer(self, id="", title="Zope OAI Server", autopublish=1, update_time=18000, autopublishRoles = [], REQUEST=None, RESPONSE=None):
    """ method for adding a new Zope OAI Server """
    if id == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'You%20have%20to%20choose%20a%20title')
            return None
    try:
        OAIO = ZopeOAIServer(id, title, update_time, autopublish, autopublishRoles)
    except:
        import traceback
        traceback.print_exc()
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.initialize()
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')

class ZopeOAIServer(App.Management.Navigation,zOAIRepository):
    """ """
    
    meta_type = 'Zope OAI Server'
    # meta_types = [ 'Open Archive Site' ] 


    manage_options= (
        {'label': 'Contents',     
         'action': 'manage_main'
         },
        {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },
        
        {'label': 'Info',     
         'action': 'manage_repositoryInfo' 
         },
        
        {'label': 'Update',     
         'action': 'manage_repositoryUpdate' 
         },
        )

    def __init__(self, id, title, update_time, autopublish, autopublishRoles):
        """ """
        self.def_autopublish = autopublish
        self.def_autopublishRoles = autopublishRoles
        self.namespaces = None
        # self.id, self.title, self.def_update        
        #  done in superclass
        try:
            zOAIRepository.__init__(self, id, title, update_time)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            zOAIRepository.__init__.im_func(self, id, title, update_time)

    def initialize(self):
        """ """
        try:
            zOAIRepository.initialize(self)
        except:
            import traceback
            traceback.print_exc()
            # this is needed for some reason when python
            # version is < 2.2
            zOAIRepository.initialize.im_func(self)

    def get_myContainer(self):
        """ """
        return self.aq_parent

    def get_namespaceList(self, attr='Schema'):
        """
        return list of the named attribute for all namespaces
          either Schema, Shortname, Namespace, Description, Prefix
        """
        nStor = self.get_myNamespaceStorage()
        list = []
        for ns_obj in nStor.objectValues():
            list.append( apply( getattr(ns_obj, 'get_ns'+attr),( )))
        return list

    def update_theRepository(self, force_update=0):
        """
        update the object as necessary
        """
        number_of_minutes_in_day = 1440

        # get all harvester objects, send update command
        #   if it is time to update them
        time_now = DateTime.DateTime()
        for item in self.get_myCatalog().searchResults({ 'meta_type':'ZCatalog Harvester'}):
            next_update = item.last_update + ( item.update_period / number_of_minutes_in_day )
            if force_update or time_now.greaterThan( next_update ):
                zc_harvester = item.getObject()
                zc_harvester.update_ZCatalogHarvester()

        # update timestamp
        self.earliestDatestamp(self.get_earliestDatestamp())
        self.commit_Changes()

        # do stuff of my parent
        # don't have any parent
        ZopeOAIServer.inheritedAttribute('update_theRepository')(self, force_update=force_update)
    update = update_theRepository

    def add_Indexes(self, cat):
        """
        """
        # general searching - from web form
        cat.addIndex('OAI_Date', 'FieldIndex')
        # cat.addIndex('OAI_Date', 'DateIndex')
        cat.addIndex('OAI_Fulltext', 'TextIndex')
        cat.addIndex('OAI_Title', 'TextIndex')

        # OAI Search stuff -
        cat.addIndex('OAI_Identifier', 'FieldIndex')
        cat.addIndex('OAI_Set', 'KeywordIndex')
        cat.addIndex('status', 'FieldIndex')
        cat.addIndex('OAI_MetadataFormat', 'FieldIndex')

        # dc search indexes
        cat.addIndex('dc_title', 'TextIndex')
        cat.addIndex('dc_creator', 'KeywordIndex')
        cat.addIndex('dc_author', 'KeywordIndex')
        cat.addIndex('dc_subject', 'TextIndex')
        cat.addIndex('dc_description', 'TextIndex')
        cat.addIndex('dc_date', 'KeywordIndex')

        # lom search indexes
        # zope searching - in code
        cat.addIndex('last_update', 'FieldIndex')
        try:
            cat.addIndex('meta_type', 'FieldIndex')
        except:
            pass

        cat.addIndex('expiration', 'FieldIndex')
        # add lexicon to new type of zcatalog
        # this isn't working right now
        #   changed to regular zcatalog
##        title_extras = Empty()
##        title_extras.doc_attr = 'OAI_Title'
##        title_extras.index_type = 'Okapi BM25 Rank'
##        title_extras.lexicon_id = 'Lexicon'
##        cat.addIndex('OAI_Title', 'ZCTextIndex', title_extras)

##        fulltext_extras = Empty()
##        fulltext_extras.doc_attr = 'OAI_Fulltext'
##        fulltext_extras.index_type = 'Okapi BM25 Rank'
##        fulltext_extras.lexicon_id = 'Lexicon'
##        cat.addIndex('OAI_Fulltext', 'ZCTextIndex', fulltext_extras)

    def add_MetadataColumns(self, cat):
        """
        """
        # check for columns that are automatically
        # added by ZCatalog module
        #
        try:
            cat.manage_addColumn('id')
        except:
            pass
        try:
            cat.manage_addColumn('title')
        except:
            pass

        # ZOAI specific columns
        cat.manage_addColumn('header')
        cat.manage_addColumn('metadata')
        cat.manage_addColumn('about')
        cat.manage_addColumn('meta_type')
        
        cat.manage_addColumn('OAI_Date')
        cat.manage_addColumn('OAI_Title')
        cat.manage_addColumn('OAI_Identifier')
        
        cat.manage_addColumn('update_period')
        cat.manage_addColumn('last_update')

        cat.manage_addColumn('dc_creator')
        cat.manage_addColumn('dc_author')
        cat.manage_addColumn('dc_description')
        cat.manage_addColumn('dc_identifier')

    ####
    #### OBJECT MANAGEMENT STUFF
    ####

    manage_main = HTMLFile("dtml/manage_ZopeOAIServerMainForm",globals())

    manage_preferences = HTMLFile("dtml/manage_ZopeOAIServerPrefsForm",globals())

    def manage_ZopeOAIServerPrefs(self, title, update_period, autopublish, autopublishRoles, repositoryName, adminEmailList, token_expiration, results_limit, REQUEST=None, RESPONSE=None):
        """ save preferences """
        self.title = title
        self.def_update = update_period
        self.def_autopublish = autopublish
        self.def_autopublishRoles = autopublishRoles
        self.repositoryName(repositoryName)
        self.adminEmail(adminEmailList)
        self.token_expiration = token_expiration
        self.results_limit = results_limit
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')
