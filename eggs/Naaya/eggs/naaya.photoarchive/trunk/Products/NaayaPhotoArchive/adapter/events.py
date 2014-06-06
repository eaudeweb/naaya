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
#   Alin Voinea, Eau de Web
""" Events
"""
from zope import event as zope_event
from OFS.event import ObjectWillBeMovedEvent, ObjectClonedEvent
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent
from zope.app.container.contained import ObjectMovedEvent, ObjectRemovedEvent, ObjectAddedEvent
from OFS.interfaces import IObjectWillBeAddedEvent

#
# NyFSFile
#
def afterAddNyPhoto(obj, event):
    """ Photo added"""
    obj._fix_after_cut_copy(obj)

def afterCloneNyPhoto(obj, event):
    """ Photo cloned"""
    obj._fix_after_cut_copy(obj)
