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
# The Original Code is RDFCalendar version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Soren Roug, EEA
# Cornel Nitu, Finsiel Romania
# Rares Vernica, Finsiel Romania

__doc__="""RDFCalendar initialization module"""
__version__= '$Revision: 1.5 $'[11:-2]

import RDFCalendar
from App.ImageFile import ImageFile

def initialize(context):
    """RDFCalendar"""

    context.registerClass(
        RDFCalendar.RDFCalendar,
        permission='Add RDFCalendar Folder',
        constructors = (RDFCalendar.manage_addRDFCalendarForm,
                        RDFCalendar.manage_addRDFCalendar
                        ),
        icon='icons/RDFCalendar.gif',
        )
    context.registerHelp()
    context.registerHelpTitle('RDF Calendar')

# Define shared web objects that are used by products.
# This is usually (always ?) limited to images used
# when displaying an object in contents lists.
# These objects are accessed as:
#   <dtml-var SCRIPT_NAME>/misc_/Product/name
misc_ = {
    "left.gif":     ImageFile("icons/left.gif", globals()),
    "right.gif":    ImageFile("icons/right.gif", globals()),
        }
