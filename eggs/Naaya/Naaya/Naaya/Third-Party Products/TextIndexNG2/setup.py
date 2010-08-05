#!/usr/bin/env python

###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

from distutils.core import setup,Extension

import sys

if sys.maxunicode>0xffff:
    unicode_arg = "-DUNICODE_WIDTH=4"
else:
    unicode_arg = "-DUNICODE_WIDTH=2"


print unicode_arg
    
setup(name = "TextIndexNGExtensions",
      version = "2.02",
      author = "Andreas Jung",
      author_email = "andreas@andreas-jung.com",
      description = "Helper modules for TextIndexNG2: Splitter, normalizer",
      url = "http://www.zope.org/Members/ajung/TextIndexNG",
          ext_modules=[

            Extension("normalizer",
                [ "src/normalizer/normalizer.c" ],
            ),

            Extension("TXNGSplitter",
                [ "src/TXNGSplitter/TXNGSplitter.c",
                  "src/TXNGSplitter/hashtable.c",
                  "src/TXNGSplitter/dict.c" 
                ],
            ),


            Extension("indexsupport",
                [ "src/indexsupport.c" ],
            ),

        ]
        )


if sys.platform != "win32":
    ext_args = ['-Wall']
else:
    ext_args = []

extLevensthein = Extension('Levenshtein',
                           sources = ['src/python-Levenshtein-0.10/Levenshtein.c'],
                           extra_compile_args=ext_args)

setup (name = 'python-Levenshtein',
       version = '0.10',
       description = 'Python extension computing string distances and similarities.',
       author = 'David Necas (Yeti)',
       author_email = 'yeti@physics.muni.cz',
       license = 'GNU GPL',
       url = 'http://trific.ath.cx/python/levenshtein/',
       long_description = '''
Levenshtein computes Levenshtein distances, similarity ratios, generalized
medians and set medians of Strings and Unicodes.  Because it's implemented
in C, it's much faster than corresponding Python library functions and
methods.
''',
       ext_modules = [extLevensthein])

