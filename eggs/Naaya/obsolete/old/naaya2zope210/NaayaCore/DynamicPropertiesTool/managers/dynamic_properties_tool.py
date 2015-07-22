# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils

class dynamic_property(utils):
    """ """

    def __init__(self, id, searchable, name, type, required, defaultvalue, values, order):
        """ """
        self.id = id
        self.searchable = searchable
        self.name = name
        self.type = type
        self.required = required
        self.defaultvalue = defaultvalue
        self.values = values
        self.order = order

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    def render(self, default='', context=None):
        """ """
        l_html = []
        if self.type == 'string' or self.type == 'date' or self.type == 'integer' or self.type == 'float':
            l_html.append('<input type="text" name="%s:utf8:ustring" id="%s" value="%s" size="50" />' % (self.utHtmlEncode(self.id), self.utHtmlEncode(self.id), self.utHtmlEncode(default)))
        elif self.type == 'boolean':
            l_html.append('<input type="checkbox" name="%s:utf8:ustring" id="%s"' % (self.utHtmlEncode(self.id), self.utHtmlEncode(self.id)))
            if default != '' and default is not None: l_html.append(' checked')
            l_html.append(' />')
        elif self.type == 'text':
            l_html.append('<textarea name="%s:utf8:ustring" id="%s" rows="5" cols="50">' % (self.utHtmlEncode(self.id), self.utHtmlEncode(self.id)))
            l_html.append(self.utHtmlEncode(default))
            l_html.append('</textarea>')
        elif self.type == 'selection':
            values = self.values
            if type(self.values) == type({}):
                try:
                    ref_list = context.getPortletsTool().getRefListById(self.values.keys()[0]).get_list()
                    values = self.utConvertListToLines([x.title for x in ref_list])
                except:
                    values = self.values.values()[0]
            l_html.append('<select name="%s:utf8:ustring" id="%s">' % (self.utHtmlEncode(self.id), self.utHtmlEncode(self.id)))
            l_html.append('<option value=""></option>')
            for l_value in values.split('\r\n'):
                if l_value != '':
                    l_html.append('<option value="%s"' % self.utHtmlEncode(l_value))
                    if l_value == default: l_html.append(' selected')
                    l_html.append('>%s</option>' % self.utHtmlEncode(l_value))
            l_html.append('</select>')
        return ''.join(l_html)

    def getindextype(self):
        """ """
        if self.dp_type == 'boolean' or self.dp_type == 'date' or self.dp_type == 'integer' or self.dp_type == 'float' or self.dp_type == 'selection':
            return 'FieldIndex'
        else:
            return 'TextIndex'

    def getvalues(self):
        """ """
        if type(self.values) == type({}):
            return self.values.values()[0]
        else:
            return self.values

InitializeClass(dynamic_property)

class dynamic_properties_tool:
    """ """

    def __init__(self):
        """ """
        self.__dynamic_properties_definitions = {}

    def getFieldTypesList(self):
        """ """
        return ['boolean', 'string', 'date', 'integer', 'float', 'text', 'selection']

    def getDynamicPropertiesIds(self):
        """ """
        return self.__dynamic_properties_definitions.keys()

    def getDynamicProperties(self):
        """ """
        return self.__dynamic_properties_definitions.values()

    def getDynamicProperty(self, p_dp_id):
        """ """
        try:
            return self.__dynamic_properties_definitions[p_dp_id]
        except:
            return None

    def addDynamicProperty(self, id, searchable, name, type, required, defaultvalue, value, order):
        """ """
        self.__dynamic_properties_definitions[id] = dynamic_property(id, searchable, name, type, required, defaultvalue, value, order)
        self._p_changed = 1

    def updateDynamicProperty(self, id, searchable, name, type, required, defaultvalue, values, order):
        """ """
        l_dp = self.__dynamic_properties_definitions[id]
        l_dp.name = name
        l_dp.searchable = searchable
        l_dp.type = type
        l_dp.required = required
        l_dp.defaultvalue = defaultvalue
        l_dp.values = values
        l_dp.order = order
        self._p_changed = 1

    def deleteDynamicProperty(self, ids):
        """ """
        for id in ids:
            del(self.__dynamic_properties_definitions[id])
        self._p_changed = 1

    def getDynamicPropertyData(self, p_dp_id):
        """ """
        l_dp = self.getDynamicProperty(p_dp_id)
        if l_dp is not None:
            ref_list = ''
            values = l_dp.values
            if type(l_dp.values) == type({}):
                ref_list = l_dp.values.keys()[0]
                try:
                    values = self.utConvertListToLines([i.title for i in self.getPortletsTool().getRefListById(ref_list).get_list()])
                except:
                    values = l_dp.values.values()[0]
            return ['update', l_dp.id, l_dp.searchable, l_dp.name, l_dp.type, l_dp.required, l_dp.defaultvalue, values, l_dp.order, ref_list]
        else:
            return ['add', '', 0, '', '', 0, '', '', 0, '']
