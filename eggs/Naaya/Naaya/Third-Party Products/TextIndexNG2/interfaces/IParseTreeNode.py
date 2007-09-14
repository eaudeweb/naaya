###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" interface for ParseTree nodes """

from Interface import Base

class IParseTreeNode(Base):
    """ interface class for ParseTreeNode """

    def getType():  
        """ return type of node """

    def getValue():
        """ return value of node """

