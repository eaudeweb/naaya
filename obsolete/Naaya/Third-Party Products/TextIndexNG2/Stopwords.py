###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Stopwords

$Id: Stopwords.py,v 1.11 2005/05/22 15:19:30 ajung Exp $
"""

import os, re

from Products.TextIndexNG2.interfaces.IStopwords import StopwordsInterface
from indexsupport import stopwordfilter

_dir = os.path.dirname(__file__)

# illegal characters inside stop words
illegal  = re.compile('[ ]')

class StopWordException(Exception): pass

class Stopwords:
    """  class for all StopWord objects """

    __implements__ = StopwordsInterface

    def __init__(self, language, words):
        self._language = language
        self._words = {}

        if isinstance(words, dict): self._words.update(words)
        elif isinstance(words, (tuple, list)):
            for w in words: self._words[w] = None
        else:
            raise TypeError,'words must be dict, tuple or list'

    def getStopWords(self):
        keys = self._words.keys()
        keys.sort()
        return keys

    def getLanguage(self):
        return self._language

    def isStopWord(self, word):
        return self._words.has_key(word.lower())

    def process(self, words): 
        return stopwordfilter(words, self._words)

    def __repr__(self):
        return "%s (%s: %s)" % (self.__class__.__name__, 
            self.getLanguage(), self.getStopWords() )


lang_reg = re.compile('#\s*language\s*=\s*([\w]+)')
enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')

class FileStopwords(Stopwords):

    def __init__(self, filename):

        assert isinstance(filename, str)
        words, language = self.readStopWords(filename) 
        Stopwords.__init__(self, language, words)


    def readStopWords(self, filename):
        """ read a stopword file (line-by-line) from disk.
            'fname' is either relative to ./stopwords/
            or has an absolute path.
        """

        d = {}
        language = None
        encoding = None

        try:        
            f = os.path.join(_dir,'stop_words',filename) 
            lines = open(f).readlines()
        except:
            try: lines = open(filename).readlines()
            except: raise

        for l in lines: 
            if not l.strip(): continue

            mo = lang_reg.match(l)
            if mo:
                language = mo.group(1)
                continue

            mo = enc_reg.match(l)
            if mo:
                encoding= mo.group(1)
                continue

            if l.startswith('#'): continue

            word = unicode(l.strip().lower(), encoding)
            d[word] = None

        return d, language
