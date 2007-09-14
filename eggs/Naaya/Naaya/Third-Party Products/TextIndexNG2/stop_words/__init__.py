# check for converter modules

import os
from Products.TextIndexNG2.Registry import StopwordsRegistry
from Products.TextIndexNG2.Stopwords import FileStopwords
from Products.TextIndexNG2 import fast_startup

if not fast_startup:

    files = os.listdir(__path__[0])
    files = [ x for x in files if x.endswith('.txt') ]

    for fname in files:
        sw = FileStopwords(fname) 
        StopwordsRegistry.register(sw.getLanguage(), sw)

    del files
