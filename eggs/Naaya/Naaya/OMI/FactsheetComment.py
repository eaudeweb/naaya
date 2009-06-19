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
# Alex Morega, Eau de Web
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from datetime import datetime

from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.CatalogAwareness import CatalogAware
from constants import *
from utilities import *

manage_addComment_html = PageTemplateFile('zpt/comment', globals())

def manage_addComment(self, parent_name, data):
    """ Method for adding a commentary"""
    id = get_available_id(self)
    newComment = FactsheetComment(id, parent_name)
    self._setObject(id, newComment)
    comment = self._getOb(id)
    comment.edit(data)
    self.model_add_comment_notification(self.contact_email, 4, id)
    self.model_add_comment_notification(self.administrator_email, 4, id) #4 is page where the comment resides

class FactsheetComment(CatalogAware, SimpleItem):
    """Class that implements a blog commentary."""

    meta_type = 'OMI Factsheet Comment'
    security = ClassSecurityInfo()

    def __init__(self, id, parent_name):
        """ constructor """
        self.id = id
        self.parent_name = parent_name
        self.created = datetime.now()

    def edit(self, data):
        for key in data.keys():
            if key in comment_names:
                setattr(self, key, data.get(key, u''))
        self.reindex_object()

InitializeClass(FactsheetComment)