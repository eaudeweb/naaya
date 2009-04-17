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
from App.ImageFile import ImageFile

#Product imports
from constants import *
import NyForum
import NyForumTopic
import NyForumMessage

from Products.Naaya import register_content
# Register as a folder content type
register_content(
    module=NyForum,
    klass=NyForum.NyForum,
    module_methods={'manage_addNyForum': PERMISSION_ADD_FORUM},
    klass_methods={'forum_add_html': PERMISSION_ADD_FORUM},
    add_method=('forum_add_html', PERMISSION_ADD_FORUM),
)

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

    context.registerClass(
        NyForumTopic.NyForumTopic,
        permission = PERMISSION_MODIFY_FORUMTOPIC,
        constructors = (
                NyForumTopic.manage_addNyForumTopic_html,
                NyForumTopic.addNyForumTopic,
                ),
        icon = 'www/NyForumTopic.gif'
        )

    context.registerClass(
        NyForumMessage.NyForumMessage,
        permission = PERMISSION_ADD_FORUMMESSAGE,
        constructors = (
                NyForumMessage.manage_addNyForumMessage_html,
                NyForumMessage.addNyForumMessage,
                ),
        icon = 'www/NyForumMessage.gif'
        )

misc_ = {
    'NyForum.gif':ImageFile('www/NyForum.gif', globals()),
    'NyForumTopic.gif':ImageFile('www/NyForumTopic.gif', globals()),
    'NyForumMessage.gif':ImageFile('www/NyForumMessage.gif', globals()),
    'attachment.gif':ImageFile('www/attachment.gif', globals()),
}
