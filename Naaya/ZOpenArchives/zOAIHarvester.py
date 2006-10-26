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

__doc__ = """Zope OAI Site Harvester"""

import string

from Globals import HTMLFile, Persistent
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
import App
import zOAIRecord # for manage_addOAIRecord
from pyOAIMH.OAIHarvester import OAIHarvester
from pyOAIMH.OAIHarvester import HTTPLibError, ServerError

import zOAISupport  # for processId


manage_addOAIHarvesterForm = HTMLFile('dtml/manage_addOAIHarvesterForm', globals())

def manage_addOAIHarvester(self, host="", url="", title="", days=7, REQUEST=None, RESPONSE=None):
    """ method for adding a new OAI object """
    if url == "":
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'You%20have%20to%20choose%20a%20url')
            return None
    try:
         id = zOAISupport.processId(host)
         OAIS = zOAIHarvester(id, host, url, title, days)
    except:
        import traceback
        traceback.print_exc()
    self._setObject(id, OAIS)
    OAIS = getattr(self, id)
    OAIS.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')


class zOAIHarvester(OAIHarvester,App.Management.Navigation, BTreeFolder2, Persistent, Implicit):
    """ """

    meta_type = 'Open Archive Harvester'
    default_document = 'index_html'

    manage_options= (
        {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },
        
        {'label': 'Update',     
         'action': 'manage_update'
         },
        
        {'label': 'Contents',     
         'action': 'manage_main'
         },
        )

    def __init__(self, id, host, url, title, days):
        """ """
        try:
            OAIHarvester.__init__(self, host, url)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            OAIHarvester.__init__.im_func(self, host, url)
        BTreeFolder2.__init__(self,id)
        self.id = id
        self.title = title
        # update frequency in days
        self.update_period = days

    def get_myContainer(self):
        """ get my parent container """
        return self.aq_parent

    def handle_addOAIRecord(self, dom=None):
        """
        create or update <record> given its DOM node
        """
        # get record header
        #the_xml = dom.toxml('UTF-8')
        header = None
        for h in dom.childNodes:
            if hasattr(h, 'tagName') and h.tagName == 'header':
                header = h
                break
        if header == None:
            raise "no header in", dom.toxml(self.default_decoding)
        # get and process ID from record header, use
        #   the id as the name for the zope record
        id = None
        for tag in header.childNodes:
            if hasattr(tag, 'tagName') and tag.tagName == 'identifier':
                id = tag
                break

        if id == None:
            raise "no identifier in ", dom.toxml(self.default_decoding)
        else:
            identifier = self.getDOMElementText(id, encode=self.default_encoding)
        # treat identifier
        metadata_format = self.current_request['metadataPrefix'].encode(self.default_encoding)
        identifier = string.strip(identifier)
        identifier = identifier.encode(self.default_encoding) + '-' + metadata_format
        identifier = zOAISupport.processId(identifier)
        # check if record object already exists with this ID
        #   if so, do an update
        OAIR = self._getOb( identifier, None)
        if OAIR != None:
            OAIR.handle_DOM(dom)
            OAIR.reindex_object()
        else:
            zOAIRecord.manage_addOAIRecord(self, id=identifier,
                                           metadata_format=self.current_request['metadataPrefix'],
                                           dom=dom)

    ######################
    ####  ZMI Interfaces
    ######################

    manage_mainold = HTMLFile("dtml/manage_OAIHarvesterMainForm",globals())

    manage_preferences = HTMLFile("dtml/manage_OAIHarvesterPrefsForm",globals())

    def manage_OAIHarvesterPrefs(self, title, minutes, site_host, site_url, metadata_format, REQUEST=None, RESPONSE=None):
        """ save preferences """
        self.title = title
        self.update_period = minutes
        self.set_siteURL(site_url)
        self.set_siteHost(site_host)
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')


    manage_update = HTMLFile("dtml/manage_OAIHarvesterUpdateForm",globals())

    def manage_OAIHarvesterUpdate(self, REQUEST=None, RESPONSE=None):
        """ update site records, identification """
        try:
            self.do_updateSite()
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Site%20records%20updated')
        except (HTTPLibError, ServerError):
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Problem%20connecting%20to%20site')