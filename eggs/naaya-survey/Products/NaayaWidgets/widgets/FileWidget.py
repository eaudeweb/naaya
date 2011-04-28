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
# Alin Voinea, Eau de Web

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.NaayaWidgets.Widget import Widget, WidgetError, manage_addWidget
from Products.NaayaCore.managers.utils import utils

def addFileWidget(container, id="", title="String Widget", REQUEST=None, **kwargs):
    """ Contructor for String widget"""
    return manage_addWidget(FileWidget, container, id, title, REQUEST, **kwargs)

class FileWidget(Widget):
    """ String Widget """

    meta_type = "Naaya File Widget"
    meta_label = "File upload"
    meta_description = "Lets the user upload a file"
    meta_sortorder = 300
    icon_filename = 'widgets/www/widget_file.gif'

    _properties = Widget._properties + (
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Max allowed uploaded files size'},
        )

    # Constructor
    _constructors = (addFileWidget,)
    render_meth = PageTemplateFile('zpt/widget_file.zpt', globals())

    size_max = 1048576
    width = 50

    def getDatamodel(self, form):
        """Get datamodel from form"""
        attached_file = form.get(self.getWidgetId(), None)
        filename = getattr(attached_file, 'filename', None)
        if not filename:
            return None
        return attached_file

    def validateDatamodel(self, value):
        """Validate datamodel"""
        # Required
        if not value:
            if self.required:
                raise WidgetError('Value required for "%s"' % self.title)
            return
        # Max size
        if self.size_max == 0:
            return True
        read_size = len(value.read(self.size_max + 1))
        if self.required and not read_size:
            value.seek(0)
            raise WidgetError('Value required for "%s". Empty file provided.' % self.title)
        if read_size > self.size_max:
            max_size_str = utils().utShowSize(self.size_max)
            value.seek(0)
            raise WidgetError('The uploaded file for "%s" is too big, the maximum allowed size is %s bytes' % (self.title, max_size_str))

    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if datamodel is None:
            return 'No file'
        return 'File uploaded'

InitializeClass(FileWidget)

def register():
    return FileWidget
