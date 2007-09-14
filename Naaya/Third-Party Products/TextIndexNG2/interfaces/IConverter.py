###########################################################################

#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class ConverterInterface(Interface.Base):
    """ interface for converters """

    def getDescription():   
        """ return a string describing what the converter is for """

    def getType():          
        """ returns a list of supported mime-types """

    def getDependency():   
        """ return a string or a sequence of strings with external
            dependencies (external programs) for the converter
        """

    def convert(doc):
        """ convert the 'doc' (string) and return a text
            representation of 'doc'
        """

    def convert2(doc, encoding, mimetype):
        """ Perform a transformation of 'doc' to (converted_text,
            new_encoding). 'encoding' and 'mimetype' can be used by
            the converter to adjust the conversion process.
            'converted_text' is either a Python string or a Python
            unicode string. 'new_encoding' is the encoding of
            'converted_text'. It must be set to 'unicode' if the 
            converted_text is a Python unicode string.
        """
