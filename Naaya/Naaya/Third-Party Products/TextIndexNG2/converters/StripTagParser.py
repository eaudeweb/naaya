###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Code taken from Dieter Maurer's CatalogSupport Module
http://www.handshake.de/~dieter/pyprojects/zope
Thank you!

$Id: StripTagParser.py,v 1.7 2004/09/08 20:20:12 ajung Exp $
"""

from sgmllib import SGMLParser

class StripTagParser(SGMLParser):
  '''SGML Parser removing any tags and translating HTML entities.'''

  data= None

  def handle_data(self,data):
    if self.data is None: self.data=[]
    self.data.append(data)

  def __str__(self):
    if self.data is None: return ''
    return ' '.join(self.data)

