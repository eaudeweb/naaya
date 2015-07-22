###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
Module breaks out Zope specific methods and behavior.  In
addition, provides the Lexicon class which defines a word to integer
mapping.

$Id: StandardLexicon.py,v 1.42 2004/11/29 19:27:20 ajung Exp $
"""

import re

from Persistence import Persistent
import BTrees.Length
from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree

from Levenshtein import ratio
from Products.TextIndexNG2.interfaces.ILexicon import LexiconInterface
from Products.TextIndexNG2.BaseParser import QueryParserError


class Lexicon(Persistent):
    """Maps words to word ids """

    __implements__ = LexiconInterface

    def __init__(self, truncate_left=0):
        self.truncate_left = truncate_left
        self.clear()

    def clear(self):
        self._nextid      = BTrees.Length.Length()
        self._forward_idx = OIBTree()
        self._inverse_idx = IOBTree()
        if self.truncate_left:
            self._lforward_idx = OIBTree()
        else:
            self._lforward_idx = None

    def getWordIdList(self, words):
        """ return a list of wordIds for a list of words """
    
        fw_idx = self._forward_idx
        fw_idx_get = fw_idx.get
        rev_idx = self._inverse_idx
        if self.truncate_left: lfw_idx = self._lforward_idx
        nextid = self._nextid

        wids = []
        append = wids.append

        for word in words:
            wid = fw_idx_get(word)
            if not wid:         
                nextid.change(1)
                wid = nextid()
                fw_idx[word] = wid
                rev_idx[wid] = word
                if self.truncate_left:
                    lfw_idx[word[::-1]] = wid
            append(wid)
        return wids

    def getWordId(self, word, default=None):
        """Return the matched word against the key."""
        return  self._forward_idx.get(word, default)

    def getWord(self, wid):
        """ return a word by its wid"""
        return self._inverse_idx[wid]

    def deleteWord(self, word):
        wid = self._forward_idx[word]
        del self._inverse_idx[wid]
        del self._forward_idx[word]

    def deleteWordId(self, wid):
        word = self._inverse_idx[wid]
        del self._forward_idx[word]
        del self._inverse_idx[wid]

    def getWordsForRightTruncation(self, prefix):
        """ Return a list for wordIds that match against prefix.
            We use the BTrees range search to perform the search
        """
        assert isinstance(prefix, unicode)
        return  self._forward_idx.keys(prefix, prefix + u'\uffff') 

    def getWordsForLeftTruncation(self, suffix):
        """ Return a sequence of word ids for a common suffix """
        suffix = suffix[::-1]
        assert isinstance(suffix, unicode)
        return  [w[::-1] for w in  self._lforward_idx.keys(suffix, suffix + u'\uffff') ] 

    def createRegex(self, pattern):
        """Translate a PATTERN to a regular expression """
        return '%s$' % pattern.replace( '*', '.*').replace( '?', '.')

    def getSimiliarWords(self, term, threshold=0.75): 
        """ return a list of similar words based on the levenshtein distance """
        return [ (w, ratio(w,term)) for w in self._forward_idx.keys() if ratio(w, term) > threshold  ]

    def getWordsForPattern(self, pattern):
        """ perform full pattern matching """

        # search for prefix in word
        mo = re.search('([\?\*])', pattern)
        if mo is None:
            return [ pattern ] 

        pos = mo.start(1)
        if pos==0: raise QueryParserError, \
            'word "%s" should not start with a globbing character' % pattern

        prefix = pattern[:pos]
        words = self._forward_idx.keys(prefix, prefix + u'\uffff')
        regex = re.compile( self.createRegex(pattern) )
        return [word  for word in words if regex.match(word) ] 

    def getWordsInRange(self, w1, w2):
        """ return all words within w1...w2 """
        return self._forward_idx.keys(w1, w2)

    def getWordsForSubstring(self, sub):
        """ return all words that match *sub* """
        return [word for word in self._forward_idx.keys() if sub in word]

    def getWordIds(self):
        """ return all wids """
        return self._inverse_idx.keys()

    def removeWordId(self, wid):
        """ remove word id 'wid' """
        word = self._inverse_idx[wid]
        del self._inverse_idx[wid]
        del self._forward_idx[word]

    def __len__(self):
        return len(self._inverse_idx.keys())

if __name__ == '__main__':
    test()
