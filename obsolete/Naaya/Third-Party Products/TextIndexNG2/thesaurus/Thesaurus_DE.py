###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import os, re
from Products.TextIndexNG2.interfaces.IThesaurus import IThesaurus

THESAURUS_FILE = os.path.join(os.path.dirname(__file__), 'de_thesaurus.txt')

# match the encoding header
enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')

class Thesaurus_DE:
    """ A german thesaurus based on the thesaurus published on www.openthesaurus.de.
        This thesaurus is published under GPL.
    """
    
    __implements__ = (IThesaurus, )

    def __init__(self):
        self._loaded = False

    def _loadThesaurus(self, filename):
        """ read thesaurus file """

        d = {}
        encoding = None

        for l in open(filename):
            if not l.strip(): continue

            mo = enc_reg.match(l)
            if mo:
                encoding= mo.group(1)
                continue

            if l.startswith('#'): continue

            term, words = l.split(' ', 1)
            if encoding:
                term = unicode(term.strip(), encoding)
                words = [unicode(w.strip(), encoding) for w in words.split(',')]
                d[term] = words  
            else:
                raise ValueError("File has no 'encoding' parameter specified")

        self.thesaurus = d
        self._loaded = True

    def getTermsFor(self, term):
        """ return a list of similiar terms for a the given term """

        if not self._loaded:
            self._loadThesaurus(THESAURUS_FILE)
        return self.thesaurus.get(term, [])

