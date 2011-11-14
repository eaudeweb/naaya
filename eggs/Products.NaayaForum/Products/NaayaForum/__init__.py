from App.ImageFile import ImageFile

from constants import *
import NyForum
import NyForumTopic
import NyForumMessage

from Products.Naaya import register_content
# Register as a folder content type
register_content(
    module=NyForum,
    klass=NyForum.NyForum,
    module_methods={'addNyForum': PERMISSION_ADD_FORUM},
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
                NyForum.addNyForum,
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
    'NyForum_marked.gif':ImageFile('www/NyForum_marked.gif', globals()),
    'NyForumTopic.gif':ImageFile('www/NyForumTopic.gif', globals()),
    'NyForumMessage.gif':ImageFile('www/NyForumMessage.gif', globals()),
    'NyForumMessage.gif':ImageFile('www/NyForumMessage.gif', globals()),
    'attachment.gif':ImageFile('www/attachment.gif', globals()),
}
