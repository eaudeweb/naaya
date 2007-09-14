###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Normalizer

$Id: Normalizer.py,v 1.13 2004/06/26 11:05:44 ajung Exp $
"""

import os, re

import normalizer
from Products.TextIndexNG2.interfaces.INormalizer import NormalizerInterface

_dir = os.path.dirname(__file__)

class Normalizer:
    """  class for all Normalizer objects """

    __implements__ = NormalizerInterface

    def __init__(self, language, lst):
        self._n = normalizer.Normalizer(lst)
        self._language = language

    def getLanguage(self):
        return self._language

    def process(self, words): 
        return self._n.normalize(words)

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, 
            self.getLanguage()  )

    def getTable(self):
        return self._n.getTable()     


lang_reg = re.compile('#\s*language\s*=\s*([\w]+)')
enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')

class FileNormalizer(Normalizer):

    def __init__(self, filename):
        lst, language = self.readNormalizer(filename) 
        Normalizer.__init__(self, language, lst)

    def readNormalizer(self, filename):
        """ read a stopword file (line-by-line) from disk.
            'fname' is either relative to ./Normalizer/
            or has an absolute path.
        """

        d = {}
        language = None
        encoding = None

        try:        
            f = os.path.join(_dir,'normalizers',filename) 
            lines = open(f).readlines()
        except:
            try: lines = open(filename).readlines()
            except: raise

        lst = []

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

            fields = l.split()
            assert len(fields) == 2
    
            k = unicode(fields[0], encoding) 
            v = unicode(fields[1], encoding) 

            lst.append( (k,v)  )

        return lst, language
