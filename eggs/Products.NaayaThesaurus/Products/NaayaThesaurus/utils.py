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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Ghica Alexandru, Finsiel Romania

#Python imports
import locale
import operator
import string

#Zope imports
from Products.NaayaCore.managers.utils import utils


class th_utils(utils):
    """ """

    def __init__(self):
        """Constructor"""
        pass

    def utIsListType(self, p_list):
        """ test if is a list """
        return type(p_list) == type([])

    def utEliminateDuplicates(self, p_objects):
        """ eliminate duplicates from a list of objects (with ids) """
        dict = {}
        for l_object in p_objects:
            dict[l_object.id] = l_object
        return dict.values()

    def utListToObj(self, p_list):
        """ """
        try:    return p_list[0]
        except: return None

    def getIdsList(self, l_data=''):
        """ """
        id_list = []
        ids = self.utConvertToList(l_data)
        for id in ids:
            id_list.append(tuple(id.split('###')))
        return id_list

    def utSortObjsByLocaleAttr(self, p_list, p_attr, p_desc=1, p_locale=''):
        """Sort a list of objects by an attribute values based on locale """
        if not p_locale:
            #normal sorting
            l_len = len(p_list)
            l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
            l_temp.sort()
            if p_desc: l_temp.reverse()
            return map(operator.getitem, l_temp, (-1,)*l_len)
        else:
            #locale sorting based
            try:
                default_locale = locale.setlocale(locale.LC_ALL)

                try:
                    #try to set for NT, WIN operating systems
                    locale.setlocale(locale.LC_ALL, p_locale)
                except:
                    #try to set for other operating system
                    if p_locale == 'ar': p_locale = 'ar_DZ'
                    else:                p_locale = '%s_%s' % (p_locale, p_locale.upper())
                    locale.setlocale(locale.LC_ALL, p_locale)

                #sorting
                l_len = len(p_list)
                l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
                l_temp.sort(lambda x, y: locale.strcoll(x[0], y[0]))
                if p_desc: l_temp.reverse()

                locale.setlocale(locale.LC_ALL, default_locale)
                return map(operator.getitem, l_temp, (-1,)*l_len)
            except:
                #in case of failure make a normal sorting
                return self.utSortObjsByLocaleAttr(p_list, p_attr, p_desc)

    def utSortListByLocale(self, p_list, p_desc, p_locale=''):
        """Sort a list of touples based on locale """
        if not p_locale:
            #normal sorting
            l_len = len(p_list)
            l_list = []
            l_append = l_list.append
            for x in p_list:
                l_append(x[0])
            l_temp = map(None, l_list, xrange(l_len), p_list)
            l_temp.sort()
            if p_desc: l_temp.reverse()
            return map(operator.getitem, l_temp, (-1,)*l_len)
        else:
            #locale sorting based
            try:
                default_locale = locale.setlocale(locale.LC_ALL)

                try:
                    #try to set for NT, WIN operating systems
                    locale.setlocale(locale.LC_ALL, p_locale)
                except:
                    #try to set for other operating system
                    if p_locale == 'ar': p_locale = 'ar_DZ'
                    else:                p_locale = '%s_%s' % (p_locale, p_locale.upper())
                    locale.setlocale(locale.LC_ALL, p_locale)

                #sorting
                l_len = len(p_list)
                l_list = []
                l_append = l_list.append
                for x in p_list:
                    l_append(unicode(x[0], 'utf8'))
                l_temp = map(None, l_list, xrange(l_len), p_list)
                l_temp.sort(lambda x, y: locale.strcoll(x[0], y[0]))
                if p_desc: l_temp.reverse()

                locale.setlocale(locale.LC_ALL, default_locale)
                return map(operator.getitem, l_temp, (-1,)*l_len)
            except:
                #in case of failure make a normal sorting
                return self.utSortListByLocale(p_list, 0)