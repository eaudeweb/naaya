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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania

__version__='$Revision: 1.6 $'[11:-2]

from App.ImageFile import ImageFile

import EventCalendar

def initialize(context):
    """ Event calendar """

    # Event calendar
    context.registerClass(
        EventCalendar.EventCalendar,
        constructors=(EventCalendar.manage_addEventCalendar_html,
                       EventCalendar.manage_addEventCalendar),
        icon='www/event_calendar.gif',
        )

misc_ = {
    'event_calendar.gif':ImageFile('www/event_calendar.gif', globals()),
    }
