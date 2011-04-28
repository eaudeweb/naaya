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
# Cristian Ciupitu, Eau de Web

import glob
import os.path

from Products.NaayaWidgets.constants import PERMISSION_ADD_WIDGETS

def _get_available_widgets():
    """ Return available widgets in current dir."""
    current_dir = os.path.dirname(__file__)
    modules = [i.split('.')[0] for i in glob.glob1(current_dir, "*.py")]
    widgets = []
    for module in modules:
        widget = __import__(module, globals(),  locals())
        if not hasattr(widget, 'register'):
            continue
        widget = widget.register()
        widgets.append(widget)
    return widgets

AVAILABLE_WIDGETS = _get_available_widgets()
AVAILABLE_WIDGETS.sort(lambda x, y: cmp(x.meta_sortorder, y.meta_sortorder)) # predictible order
AVAILABLE_WIDGETS = tuple(AVAILABLE_WIDGETS) # make it readonly and suitable for isinstance

def register_widget(context, widget):
    """ Register given widget to context"""
    context.registerClass(
        widget,
        constructors = widget._constructors,
        permission = PERMISSION_ADD_WIDGETS,
        icon = getattr(widget, 'icon_filename', 'www/widget.gif'))

def initialize(context):
    """Called at zope startup"""
    global AVAILABLE_WIDGETS
    for widget in AVAILABLE_WIDGETS:
        register_widget(context, widget)
