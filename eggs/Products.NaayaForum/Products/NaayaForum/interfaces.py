from zope.interface import Interface, Attribute

class INyForumObjectAddEvent(Interface):
    """ Event triggered when a forum object is added """

    context = Attribute("The new forum topic or message")
    contributor = Attribute("user_id of user who made the changes")

class INyForumTopicAddEvent(INyForumObjectAddEvent):
    """ Event triggered when a forum topic is added """

class INyForumMessageAddEvent(INyForumObjectAddEvent):
    """ Event triggered when a forum message is added """


class INyForumObjectEditEvent(Interface):
    """ Event triggered when a forum object is edited """

    context = Attribute("The forum topic or message")
    contributor = Attribute("user_id of user who made the changes")

class INyForumTopicEditEvent(INyForumObjectEditEvent):
    """ Event triggered when a forum topic is edited """

class INyForumMessageEditEvent(INyForumObjectEditEvent):
    """ Event triggered when a forum message is edited """

class INyForum(Interface):
    pass

class INyForumTopic(Interface):
    pass
