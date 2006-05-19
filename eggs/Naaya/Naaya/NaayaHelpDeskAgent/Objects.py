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

# Objects included in HelpDesk instances
# Managed from the Zope Console, 'Administration' tab

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product improts
from Toolz import *
from Constants import *


class IssuePriority:
    """Define IssuePrioritiy for REQUESTS"""

    def __init__(self, id, title, description, value):
        """Init a new IssuePriority object"""
        self.id = id
        self.title = title
        self.description = description
        self.value = int(value)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(IssuePriority)

class IssueStatus:
    """Define IssueStatus for REQUESTS"""

    def __init__(self, id, title, description, order):
        """Init a new IssuePriority object"""
        self.id = id
        self.title = title
        self.description = description
        self.order = int(order)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(IssueStatus)

class IssueSendType:
    """Define IssueSendType for REQUESTS
      - how a issue was submitted (by phone, by email, by web form ...)"""

    def __init__(self, id, title, description):
        """Init a new IssueSendType object"""
        self.id = id
        self.title = title
        self.description = description

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(IssueSendType)

class IssueCategory:
    """Define IssueCategory of REQUESTS"""

    def __init__(self, id, title, description, priority, advice, advicelink, issuesconsultant):
        """Init a new IssueCategory object"""
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.advice = advice
        self.advicelink = advicelink
        self.issuesconsultant = issuesconsultant

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(IssueCategory)

class IssueComment:
    """Define IssueComment"""

    def __init__(self, id, date, username, content_type, content):
        """Init a new IssueComment object"""
        self.id = id
        self.date = date
        self.username = username
        self.content_type = content_type   #1 - plain text, 0 - html
        self.content = content

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(IssueComment)

class IssueHistory:
    """Define IssueHistory"""

    def __init__(self, id, date, username, action, status, priority, consultant, comments):
        """Inita new IssueHistory object"""
        self.id = id
        self.date = date
        self.username = username
        self.action = action
        self.status = status
        self.priority = priority
        self.consultant = consultant
        self.comments = comments

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(IssueHistory)

class User:
    """Define an User for HelpDesk system"""

    def __init__(self, id, zope_user, first_name, last_name, email, role):
        """Init a new User object"""
        self.id = id
        self.zope_user = zope_user
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = ConvertToList(role)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(User)
