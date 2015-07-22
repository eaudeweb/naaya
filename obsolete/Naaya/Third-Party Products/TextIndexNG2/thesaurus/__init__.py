###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

from Products.TextIndexNG2.Registry import ThesaurusRegistry
from Products.TextIndexNG2 import fast_startup

from ExampleThesaurus import ExampleThesaurus
from Thesaurus_DE import Thesaurus_DE 

if not fast_startup:
    ThesaurusRegistry.register('ExampleThesaurus', ExampleThesaurus())
    ThesaurusRegistry.register('german', Thesaurus_DE())
