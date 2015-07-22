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
# The Original Code is Naaya version 1.0
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

"""
This module contains a class for customizing attribute access.
It is used to provide values for two catalog indexes:

    - B{objectkeywords_I{lang}} where lang is the a language code

    - B{istranslated_I{lang}} where lang is the a language code
"""

#Python imports

#Zope imports

#Product imports
from Products.NaayaBase.NyContentType import NyContentType

class NyAttributes:
    """ """

    def get_meta_label(self):
        if isinstance(self, NyContentType):
            return NyContentType.get_meta_label(self)
        elif hasattr(self, 'meta_label'):
            return self.meta_label
        else:
            return self.meta_type

    def __getattr__(self, name):
        """
        Called when an attribute lookup has not found the attribute in the usual places.
        @param name: the attribute name
        @return: should return the attribute value or raise an I{AttributeError} exception.
        """
        if name.startswith('objectkeywords_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.objectkeywords(lang)
        elif name.startswith('istranslated_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.istranslated(lang)
        elif name.startswith('coverage_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.getLocalProperty('coverage', lang)
        elif name.startswith('tags_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.tags(lang)
        raise AttributeError, name
