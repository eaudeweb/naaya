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

#Product imports
from os.path import join, dirname
import zLOG
from Products.LocalFS.LocalFS import manage_addLocalFS

def initialize(context):
    """ Register extjs lib"""
    app = context._ProductContext__app
    extjs_lib = getattr(app, 'extjs', None)
    # Already installed
    if extjs_lib:
        return
    manage_addLocalFS(app, 'extjs', 'ExtJs Library', join(dirname(__file__), 'extjs'))
    zLOG.LOG('Naaya.managers', zLOG.INFO, 'ExtJs Library registered')
