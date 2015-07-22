# check for converter modules

import StandardLexicon
from Products.TextIndexNG2.Registry import LexiconRegistry

LexiconRegistry.register('StandardLexicon', StandardLexicon.Lexicon)
