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
from zOAIRepository import zOAIRepository


manage_addOAIAggregatorForm = HTMLFile('dtml/manage_addOAIAggregatorForm', globals())

def manage_addOAIAggregator(self, id="", title="OAI Aggregator", minutes=18000, REQUEST=None, RESPONSE=None):
    """ method for adding a new OAI Aggregator """

    if id == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20titre')
            return None

    try:
        OAIO = zOAIAggregator(id, title, minutes)
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?updat_menu=1')



class zOAIAggregator(zOAIRepository):
    """ """

    meta_type = 'Open Archive Aggregator'

    manage_main = HTMLFile("dtml/manage_OAIAggregatorMainForm",globals())

    def add_Indexes(self, cat):
        """
        """
        # general searching - from web form
        #cat.addIndex('OAI_Date', 'DateIndex')
        cat.addIndex('OAI_Date', 'FieldIndex')
        try:
            OAI_Fulltext_extras = Empty()
            OAI_Fulltext_extras.doc_attr = 'OAI_Fulltext'
            OAI_Fulltext_extras.index_type = 'Okapi BM25 Rank'
            OAI_Fulltext_extras.lexicon_id = 'Lexicon'
            cat.addIndex('OAI_Fulltext', 'ZCTextIndex', OAI_Fulltext_extras)
        except:
            import traceback
            traceback.print_exc()
            cat.addIndex('OAI_Fulltext', 'TextIndex')
        try:
            OAI_Title_extras = Empty()
            OAI_Title_extras.doc_attr = 'OAI_Title'
            OAI_Title_extras.index_type = 'Cosine Measure'
            OAI_Title_extras_extras.lexicon_id = 'Lexicon'
            cat.addIndex('OAI_Title', 'ZCTextIndex', OAI_Title_extras)
        except:
            cat.addIndex('OAI_Title', 'TextIndex')
        try:
            dc_creator_extras = Empty()
            dc_creator_extras.doc_attr = 'dc_creator'
            dc_creator_extras.index_type = 'Cosine Measure'
            dc_creator_extras.lexicon_id = 'Lexicon'
            cat.addIndex('dc_creator', 'ZCTextIndex',dc_creator_extras)
        except:
            cat.addIndex('dc_creator', 'TextIndex')
        try:
            dc_author_extras = Empty()
            dc_author_extras.doc_attr = 'dc_author'
            dc_author_extras.index_type = 'Cosine Measure'
            dc_author_extras.lexicon_id = 'Lexicon'
            cat.addIndex('dc_author', 'ZCTextIndex',dc_author_extras)
        except:
            cat.addIndex('dc_author', 'TextIndex')
        try:
            dc_description_extras = Empty()
            dc_description_extras.doc_attr = 'dc_description'
            dc_description_extras.index_type = 'Okapi BM25 Rank'
            dc_description_extras.lexicon_id = 'Lexicon'
            cat.addIndex('dc_description', 'ZCTextIndex',dc_description_extras)
        except:
            cat.addIndex('dc_description', 'TextIndex')
        try:
            dc_type_extras = Empty()
            dc_type_extras.doc_attr = 'dc_type'
            dc_type_extras.index_type = 'Cosine Measure'
            dc_type_extras.lexicon_id = 'Lexicon'
            cat.addIndex('dc_type', 'ZCTextIndex',dc_type_extras)
        except:
            cat.addIndex('dc_type', 'TextIndex')
        cat.addIndex('meta_type', 'FieldIndex')
        # OAI Search stuff -
        #
        cat.addIndex('OAI_Identifier', 'FieldIndex')
        cat.addIndex('OAI_Set', 'KeywordIndex')
        cat.addIndex('expiration', 'FieldIndex')

    def add_MetadataColumns(self, cat):
        """
        """
        try:
            cat.manage_addColumn('id')
        except:
            pass
        try:
            cat.manage_addColumn('title')
        except:
            pass

        cat.manage_addColumn('header')
        cat.manage_addColumn('metadata')
        cat.manage_addColumn('OAI_Date')
        cat.manage_addColumn('OAI_Title')
        cat.manage_addColumn('OAI_Identifier')
        cat.manage_addColumn('dc_creator')
        cat.manage_addColumn('dc_author')
        cat.manage_addColumn('dc_type')
        cat.manage_addColumn('dc_identifier')
        cat.manage_addColumn('dc_description')

    def getHarvesters(self):
        """ """
        harvesters_list =[]
        harvesters = self.objectItems('Open Archive Harvester')
        for i in range(len(harvesters)):
            harvesters_list.append(harvesters[i][1])
        return harvesters_list

    manage_preferences = HTMLFile("dtml/manage_OAIAggregatorPrefsForm",globals())

    def manage_OAIRepositoryPrefs(self, title, updat_period, token_expiration, results_limit, REQUEST=None, RESPONSE=None):
        """ save preferences """
        self.title = title
        self.def_updat = updat_period
        self.token_expiration = token_expiration
        self.results_limit = results_limit
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')


##########
# empty class for creation of catalog initialization
#

class Empty: pass
