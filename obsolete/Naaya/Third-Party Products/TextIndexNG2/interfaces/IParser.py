###########################################################################

#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class ParserInterface(Interface.Base):
    """ interface for TextIndexNG query parsers """

    def getDescription():
        """ return a string with a description of the parser """
   
    def getId():       
        """ return Id of parser """

    def parse(query, operator):
        """ translate the 'query' into a valid Python expression according
            to the query parser specification. 
        """
