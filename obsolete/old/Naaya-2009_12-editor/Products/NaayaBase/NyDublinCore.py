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
# Dragos Chirila, Finsiel Romania


"""
This module contains the class that provides Dublin Core elements.
"""

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass

#Product imports
from constants import *
from NyCheckControl import NyCheckControl

class NyDublinCore:
    """
    The class that provides Dublin Core elements.
    """

    def __init__(self):
        """
        Initialize variables.
        """
        pass

    security = ClassSecurityInfo()

    security.declarePublic('format')
    def format(self):
        """
        The physical or digital manifestation of the resource.
        """
        return 'text/html'

    security.declarePublic('type')
    def type(self):
        """
        The nature or genre of the content of the resource.
        """
        return 'Text'

    security.declarePublic('identifier')
    def identifier(self):
        """
        An unambiguous reference to the resource within a given context.
        """
        return self.absolute_url()

    security.declarePublic('language')
    def language(self):
        """
        A language of the intellectual content of the resource.
        """
        return self.gl_get_selected_language()

InitializeClass(NyDublinCore)
