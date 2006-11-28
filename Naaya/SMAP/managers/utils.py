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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports
import locale
import operator


def utSortObjsByLocaleAttr(p_list, p_attr, p_desc=1, p_locale=''):
    """Sort a list of objects by an attribute values based on locale"""
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
            locale.setlocale(locale.LC_ALL, default_locale)
            return utSortObjsByLocaleAttr(p_list, p_attr, p_desc)
