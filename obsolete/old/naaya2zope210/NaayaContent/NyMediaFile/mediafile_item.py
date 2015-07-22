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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Alin Voinea, Eau de Web

#Python imports
from Acquisition import Implicit

#Zope imports

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyContentType import NyContentData

class mediafile_item(Implicit, NyContentData):
    """ """

    subtitle = LocalProperty('subtitle')
