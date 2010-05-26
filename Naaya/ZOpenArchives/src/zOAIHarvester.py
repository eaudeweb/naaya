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
from urllib import quote

from Globals import HTMLFile, Persistent
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
import App

from zOAIRecord import manage_addOAIRecord
from zOAISupport import processId
from pyOAIMH.OAIHarvester import OAIHarvester
from pyOAIMH.OAIHarvester import ServerError

manage_addOAIHarvesterForm = HTMLFile('dtml/manage_addOAIHarvesterForm', globals())

def manage_addOAIHarvester(self, id='', REQUEST=None, **kwargs):
    """ Add a Harverster Object """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)

    if form_data.get('host', '') == '' or form_data.get('url', '') == '':
        error = "host and url fields are required"
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST.get('HTTP_REFERER', self.absolute_url() + '/manage_main?') + '&error_message=%s' % quote(error))
        else:
            raise ValueError(error)

    if id == '':
        id = processId(form_data['host'])

    OAIS = zOAIHarvester(id, form_data['host'], form_data['url'], form_data.get('title', ''), form_data.get('days', 7))
    self._setObject(id, OAIS)

    OAIS = getattr(self, id)
    OAIS.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')

class zOAIHarvester(OAIHarvester, App.Management.Navigation, BTreeFolder2, Persistent, Implicit):
    """ """

    meta_type = 'Open Archive Harvester'
    default_document = 'index_html'

    manage_options= (
        {'label': 'Preferences', 'action': 'manage_preferences'},
        {'label': 'Update', 'action': 'manage_update'},
        {'label': 'Contents', 'action': 'manage_main' },
    )

    def __init__(self, id, host, url, title, days):
        """ """
        super(zOAIHarvester, self).__init__(host, url)
        BTreeFolder2.__init__(self, id)

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
            manage_addOAIRecord(self, id=identifier,
                                           metadata_format=self.current_request['metadataPrefix'],
                                           dom=dom)

    ######################
    ####  ZMI Interfaces
    ######################

    manage_mainold = HTMLFile("dtml/manage_OAIHarvesterMainForm", globals())

    manage_preferences = HTMLFile("dtml/manage_OAIHarvesterPrefsForm", globals())

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
        except ServerError:
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Problem%20connecting%20to%20site')
