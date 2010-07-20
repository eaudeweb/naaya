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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

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
