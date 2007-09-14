# Waahh...check for Zope 2.5 Zope splitters
# and add some wrappers for splitters

from Products.TextIndexNG2.Registry import SplitterRegistry
from TXNGSplitter import TXNGSplitter

SplitterRegistry.register('TXNGSplitter', TXNGSplitter)
