###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################


""" interface for registries """

from Interface import Base


class RegistryInterface(Base):
    """ interface for registries """

    def getRegisteredObject(id):
        """ return a class or instance for id """

    def getRegisteredObjects():
        """ return sequence of all registered objects"""

    def is_registered(id):
        """ return 1 is registry has a key id,
            else 0 
        """

    def register(id, instance=None):
        """ register a class or instance as id """

    def unregister(id):
        """ unregister id """

    def allRegisteredObjects():
        """ return a sequence of all registered classes
            or instances 
        """

    def allIds():
        """ return a sequence of all registered ids """

