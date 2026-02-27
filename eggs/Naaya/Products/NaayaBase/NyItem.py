"""
This module contains the class that implements the Naaya simple item type of object.
All types of objects that are not containers must extend this class.
"""

from zope.interface import implementer
from OFS.SimpleItem import SimpleItem
from AccessControl.class_init import InitializeClass
from AccessControl import ClassSecurityInfo

from .interfaces import INyItem
from .NyBase import NyBase
from .NyPermissions import NyPermissions
from .NyComments import NyCommentable
from .NyDublinCore import NyDublinCore

@implementer(INyItem)
class NyItem(SimpleItem, NyCommentable, NyBase, NyPermissions, NyDublinCore):
    """
    Class that implements the Naaya simple item type of object.
    """


    manage_options = (
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Constructor.
        """

        NyBase.__dict__['__init__'](self)
        NyDublinCore.__dict__['__init__'](self)

InitializeClass(NyItem)
