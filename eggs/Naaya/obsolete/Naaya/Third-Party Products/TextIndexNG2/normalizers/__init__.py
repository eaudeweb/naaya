###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################


# check for parser modules

import os
from Products.TextIndexNG2.Registry import NormalizerRegistry
from Products.TextIndexNG2.Normalizer import FileNormalizer
from Products.TextIndexNG2 import fast_startup


if not fast_startup:

    _oldcwd = os.getcwd()

    os.chdir(__path__[0])
    files = os.listdir('.')
    files = [ x   for x in files if x.endswith('.txt') ] 

    for f  in files:

        n = FileNormalizer(f)
        try: NormalizerRegistry.register(n.getLanguage(), n) 
        except: 
            pass

    os.chdir(_oldcwd)
