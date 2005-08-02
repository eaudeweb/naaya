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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports

#Product imports

class NyAttributes:
    """ """

    def __getattr__(self, name):
        #used by the catalog to index objects
        if name.startswith('objectkeywords_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.objectkeywords(lang)
        elif name.startswith('istranslated_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.istranslated(lang)
        raise AttributeError, name
