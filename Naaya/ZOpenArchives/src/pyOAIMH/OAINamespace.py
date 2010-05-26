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

__doc__ = """ OAI Namespace object module  """

# this is for saving namespace information for repositories
#

oai_dc_defaults = {
    'schema':'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
    'prefix':'oai_dc',
    'description':'Open Archives Initiative metadata format based on Dublin Core',
    'namespace':'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'shortname':'OAI Dublin Core',
    }


class OAINamespace:

    def __init__(self, ns_prefix=None, ns_description=None, ns_shortname=None, ns_schema=None, ns_namespace=None):
        """ """
        self.ns_schema = ns_schema
        self.ns_shortname = ns_shortname
        self.ns_description = ns_description
        self.ns_prefix = ns_prefix
        self.ns_namespace = ns_namespace



    ############
    #### accessor methods

    #### schema
        
    def get_nsSchema(self):
        """ """
        return self.ns_schema

    def set_nsSchema(self, value):
        """ """
        self.ns_schema = value
        
    #### name
        
    def get_nsShortname(self):
        """ """
        return self.ns_shortname

    def set_nsShortname(self, value):
        """ """
        self.ns_shortname = value

    #### description

    def get_nsDescription(self):
        """ """
        return self.ns_description

    def set_nsDescription(self, value):
        """ """
        self.ns_description = value

    #### prefix
 
    def get_nsPrefix(self):
        """ """
        return self.ns_prefix


    def set_nsPrefix(self, value):
        """ """
        self.ns_prefix = value
              
    #### namespace
 
    def get_nsNamespace(self):
        """ """
        return self.ns_namespace


    def set_nsNamespace(self, value):
        """ """
        self.ns_namespace = value
             

    def get_nsDictionary(self):
        """ """ 
        dict = {}
        dict['description'] = self.ns_description
        dict['shortname'] = self.ns_shortname
        dict['namespace'] = self.ns_namespace
        dict['prefix'] = self.ns_prefix
        dict['schema'] = self.ns_schema       
        return dict
