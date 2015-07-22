###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import re
from entities2uc import entitydefs

# Matches entities
entity_reg = re.compile('&(.*?);')

def handler(x):
    """ Callback to convert entity to UC """
    v = x.group(1)
    return entitydefs.get(v, '')

def convert_entities(text):
    """ replace all entities inside a unicode string """
    assert isinstance(text, unicode)
    text = entity_reg.sub(handler, text)
    return text

