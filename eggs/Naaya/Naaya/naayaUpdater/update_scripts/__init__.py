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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web


#Python imports
import os

#Zope imports
import Acquisition
from OFS.SimpleItem import Item

#Naaya imports

class UpdateScript(Item, Acquisition.Implicit):
    """ """
    update_id = 'UpdateScript'
    title = 'Main class for update scripts'


def register_scripts(updater):
    for filename in os.listdir(os.path.dirname(__file__)):
        if not (filename.startswith('update_') and filename.endswith('.py')):
            continue
        objects = __import__(filename[:-3], globals(), None, ['*'])
        for key, obj in objects.__dict__.iteritems():
            if (isinstance(obj, type) and issubclass(obj, UpdateScript) and
                    obj not in (UpdateScript, )):
                updater.register_update_script(obj.update_id, obj)

