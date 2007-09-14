###########################################################################

#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Base parser class

$Id: BaseParser.py,v 1.9 2003/07/09 17:33:47 ajung Exp $
"""

from interfaces.IParser import ParserInterface

class QueryParserError(Exception):
    """ """    

class BaseParser:
    """ Base class for all parsers """

    __implements__ = ParserInterface

    id = None
    parser_description = None

    def getDescription(self):   return self.parser_description
    def getId(self):            return self.id
    def __call__(self, query, operator=''):
        return self.parse(query, operator)
    
