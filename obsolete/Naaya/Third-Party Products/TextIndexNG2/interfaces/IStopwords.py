###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class StopwordsInterface(Interface.Base):
    """ interface to stopwords """

    def getLanguage():    """ return the language of the stop words """
    
    def isStopWord(word): """ returns 1 if word is a stop word, else 0 """

    def getStopWords():   """ return a list of all stop words """

    def process(words):   """ filter out all stop words from a sequence of words """
