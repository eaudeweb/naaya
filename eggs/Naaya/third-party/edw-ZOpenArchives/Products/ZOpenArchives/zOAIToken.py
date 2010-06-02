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

__doc__ = """ Zope OAI Resumption Token """




import urllib
import string
import DateTime
import random

import Globals
from Globals import HTMLFile
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
# from Products.PTKBase.PortalContent import PortalContent
from OFS.SimpleItem import SimpleItem

from utils import processId


def manage_addOAIToken(self, parent_id=None, request_args={}, token_args={}):
    """ """
    ran_num = random.random()
    time = DateTime.DateTime().millis()
    #id = str(ran_num) + '_' + str(time)
    id = str(time)
    try:
         id = processId(id)
         OAIT = zOAIToken(id, parent_id=parent_id, request_args=request_args, token_args=token_args)
    except:
        import traceback
        traceback.print_exc()
    self._setObject(id, OAIT)
    OAIT = getattr(self, id)
    OAIT.index_object()
    return OAIT

class zOAIToken(SimpleItem, Implicit):
    """ """
    meta_type = 'zOAI Token'
    default_document = 'index_html'
    default_catalog = 'OAI_Catalog'

    index_html = HTMLFile("dtml/manage_OAITokenForm",globals())

    manage_options= (
        {'label': 'Contents',
         'action': 'index_html'
         },
        )

    def __init__(self, id, parent_id=None, request_args={}, token_args={}):
        """ """
        self.id = id
        if not token_args.has_key('id'):
            token_args['id'] = id
        self.expiration = token_args['expirationDate']
        self.parent_id = parent_id
        self.request_args = request_args
        self.token_args = token_args

    def get_RequestArgs(self):
        """ """
        return self.request_args

    def get_TokenArgs(self):
        """ """
        return self.token_args

    def get_RequestArg(self, name):
        """ """
        value = None
        if self.request_args.has_key(name):
            value = self.request_args[name]
        return value

    def get_TokenArg(self, name):
        """ """
        value = None
        if self.token_args.has_key(name):
            value = self.token_args[name]
        return value

    def index_object(self):
        """
        """
        getattr(self, self.default_catalog).catalog_object(self, urllib.unquote('/' + self.absolute_url(1) ))

    def unindex_object(self):
        """
        """
        getattr(self, self.default_catalog).uncatalog_object(urllib.unquote('/' + self.absolute_url(1) ))

    def reindex_object(self):
        """
        """
        self.unindex_object()
        self.index_object()

    def manage_beforeDelete(self, item, container):
        """ do stuff before being deleted """
        # remove object from catalog
        #
        self.unindex_object()
        SimpleItem.inheritedAttribute("manage_beforeDelete")(self,item,container)
