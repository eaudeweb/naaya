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
from ImageFile import ImageFile

#Product imports
from constants import *
import NyForum

def initialize(context):
    """ """

    #register classes
    context.registerClass(
        NyForum.NyForum,
        permission = PERMISSION_ADD_FORUM,
        constructors = (
                NyForum.manage_addNyForum_html,
                NyForum.manage_addNyForum,
                ),
        icon = 'www/NyForum.gif'
        )

misc_ = {
    'NyForum.gif':ImageFile('www/NyForum.gif', globals()),
    'NyForumTopic.gif':ImageFile('www/NyForumTopic.gif', globals()),
    'NyForumMessage.gif':ImageFile('www/NyForumMessage.gif', globals()),
    'attachment.gif':ImageFile('www/attachment.gif', globals()),
}
