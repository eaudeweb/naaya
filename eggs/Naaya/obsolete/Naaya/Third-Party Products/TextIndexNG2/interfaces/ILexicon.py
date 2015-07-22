###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class LexiconInterface(Interface.Base):
    """ Interface for Lexicon objects """

    def getWordIdList(words):
        """ return a list a wordIds for a list of words """

    def getWordId(word, default=None):
        """Return the wordId for 'word' """
    
    def getWord(wid):
        """ return the word for the given word ID"""

    def getWordsForRightTruncation(prefix):
        """ return a sequence of words with a given prefix
        """

    def getWordsForLeftTruncation(suffix):
        """ return a sequence of words with a common suffix
        """

    def getWordsForPattern(pattern):
        """ return a sequence of words that match 'pattern'.
           'pattern' is a sequence of characters including 
           the wildcards '?' and '*'.
        """         

    def getWordsInRange(w1, w2):
        """ return a sorted list of words where
            w1 <= w(x) <= w2.
        """

    def getSimiliarWords(term, threshold):
        """  return a list of that are similar basedon the Levenshtein distance """

    def getWordsForSubstring(sub):
        """ return all words that match the given substring """

    def getWordIds():
        """ return all wids """

    def removeWordId(wid):
        """ remove word id 'wid' """
