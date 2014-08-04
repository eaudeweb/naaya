"""
This module contains the class that implements the Naaya folder type of object.
All types of objects that are containers must extend this class.

"""

from zope.interface import implements
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from interfaces import INyContainer
from NyBase import NyBase
from NyPermissions import NyPermissions
from NyComments import NyCommentable
from NyDublinCore import NyDublinCore

class NyContainer(Folder, NyCommentable, NyBase, NyPermissions, NyDublinCore):
    """ Class that implements the Naaya folder type of object. """

    implements(INyContainer)

    manage_options = (
        Folder.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self):
        """ """

        NyBase.__dict__['__init__'](self)
        NyDublinCore.__dict__['__init__'](self)

    def getObjectById(self, p_id):
        """ Returns an object inside this one with the given id. """

        return self._getOb(p_id, None)

    def getObjectByUrl(self, p_url):
        """ Returns an object inside this one with the given relative URL. """

        try: return self.unrestrictedTraverse(p_url, None)
        except: return None

    def getObjectsByIds(self, p_ids):
        """ Returns a list of objects inside this one with the given a list of
        `p_ids`

        """

        ids = map(self._getOb, p_ids)
        return [x for x in ids if x is not None]

    def getObjectsByUrls(self, p_urls):
        """ Returns a list of objects inside this one with the given relative
        paths in a form of a list.

        """

        objects = map(self.unrestrictedTraverse, p_urls)
        return [x for x in objects if x is not None]

    #restrictions
    def get_valid_roles(self):
        """
        Returns a list of roles that can be used to restrict this folder
        """

        roles = list(self.valid_roles())
        filter(roles.remove, ['Administrator', 'Anonymous', 'Manager', 'Owner'])
        return roles

    def has_restrictions(self):
        """Indicates if this folder has restrictions for the current user."""
        if self.is_public():
            return False
        return not self.acquiredRolesAreUsedBy(view)

    def get_roles_with_access(self):
        """Returns a list of roles that have access to this folder."""

        r = []
        ra = r.append
        for x in self.rolesOfPermission(view):
            if x['selected'] and x['name'] not in ['Administrator',
                 'Anonymous', 'Manager', 'Owner']:
                ra(x['name'])
        return r

    def is_public(self):
        """Indicates if this folder is public (accessible by Anonymous)."""
        for x in self.rolesOfPermission(view):
            if x['selected'] and x['name'] == 'Anonymous':
                return True
        return False

    def generateItemId(self, p_prefix):
        """Returns a unique id within the container's context"""

        max_attempts = 20000
        attempts = max_attempts
        while True:
            attempts -= 1
            if not attempts: raise "IdGenerationError", "Unable to generate unique id after attempting for %s times" % max_attempts
            id = p_prefix + self.utGenRandomId(6)
            try:
                dummy = self._getOb(id)
            except:
                break
        return id

InitializeClass(NyContainer)
