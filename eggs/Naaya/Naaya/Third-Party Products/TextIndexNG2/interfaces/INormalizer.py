###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class NormalizerInterface(Interface.Base):
    """ interface for normalizers"""

    def getLanguage():    """ return the language of the stop words """

    def process(words):   """ normalize a word or a sequence of words"""

    def getTable():       """ return a sequence of tuples (old,new) strings """
