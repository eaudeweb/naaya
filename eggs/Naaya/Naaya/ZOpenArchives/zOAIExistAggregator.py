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

__doc__ = """ Zope OAI Exist Aggregator """


from Globals import HTMLFile
from AccessControl import ClassSecurityInfo
from zOAIExistRepository import zOAIExistRepository


manage_addOAIExistAggregatorForm = HTMLFile('dtml/manage_addOAIExistAggregatorForm', globals())

def manage_addOAIExistAggregator(self,
                                 id="",
                                 title="OAI Exist Aggregator",
                                 minutes=18000,
                                 existDAId='',
                                 existCollRoot = '',
                                 REQUEST=None,
                                 RESPONSE=None):
    """ method for adding a new OAI Exist Aggregator """

    if id == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20titre')
            return None
    if existCollRoot == '' or existDAId == '' or not hasattr(self, existDAId):
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20une%20collection%20et%20un%20eXistDAId%20correct')
            return None

    try:
        OAIO = zOAIExistAggregator(id,
                                   title,
                                   minutes,
                                   existDAId,
                                   existCollRoot,
                                   )
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?updat_menu=1')



class zOAIExistAggregator(zOAIExistRepository):
    """ """
    
    meta_type = 'Exist Open Archive Aggregator'

    manage_main = HTMLFile("dtml/manage_OAIExistAggregatorMainForm",globals())



