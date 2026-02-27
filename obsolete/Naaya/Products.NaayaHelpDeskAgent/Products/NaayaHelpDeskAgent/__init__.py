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
# The Original Code is HelpDeskAgent version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Dragos Chirila, Finsiel Romania


from HelpDesk import HelpDesk, manage_addHelpDeskForm, manage_addHelpDesk
from App.ImageFile import ImageFile


def initialize(context):
    """ Initialize the HelpDesk product"""
    context.registerClass(
            HelpDesk,
            constructors = (manage_addHelpDeskForm, manage_addHelpDesk),
            permission = 'Add HelpDesk',
            icon = 'www/HelpDesk.gif'
    )

misc_ = {
        'HelpDesk':ImageFile('www/HelpDesk.gif', globals()),
        'Issue':ImageFile('www/Issue.gif', globals()),
        'spacer':ImageFile('www/spacer.gif', globals()),
        'sortup.gif':ImageFile('www/sortup.gif', globals()),
        'sortdown.gif':ImageFile('www/sortdown.gif', globals()),
        'sortnot.gif':ImageFile('www/sortnot.gif', globals()),
        'new':ImageFile('www/new.gif', globals()),
        'menu_top_left':ImageFile('www/menu_top_left.gif', globals()),
        'menu_top_right':ImageFile('www/menu_top_right.gif', globals())
}
