""" This module contains the class that implements the profile sheet. """
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.NaayaCore.managers.utils import utils
from constants import METATYPE_PROFILESHEET

def manage_addProfileSheet(self, id, title='', instance_identifier='', REQUEST=None):
    """ """
    ob = ProfileSheet(id, title, instance_identifier)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class ProfileSheet(PropertyManager, SimpleItem, utils):
    """ """

    meta_type = METATYPE_PROFILESHEET
    icon = 'misc_/NaayaCore/ProfileSheet.gif'

    manage_options = (
        PropertyManager.manage_options +
        SimpleItem.manage_options
    )

    _properties=(
        {'id':'title', 'type': 'string', 'mode': 'w'},
        {'id':'instance_identifier', 'type': 'string', 'mode': 'w'},
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, instance_identifier):
        """
        Arguments:

        `instanced_identifier` -- stores a reference to the object associated
                                  with this sheet; based on this value the
                                  object can be accessed.
        """
        self.id = id
        self.title = title
        self.instance_identifier = instance_identifier

InitializeClass(ProfileSheet)
