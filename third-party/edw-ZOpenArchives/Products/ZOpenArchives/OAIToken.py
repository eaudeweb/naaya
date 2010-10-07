#No longer used
from random import randint
from Acquisition import Implicit
from OFS.SimpleItem import SimpleItem

from utils import create_object, process_form

from interfaces import IOAIToken

def manage_addOAIToken(self, id=None, **kwargs):
    """ """
    if id is None:
        id = u"%sr%s" % (int(kwargs['token_args'].get('cursor', 0)),
                          randint(10000, 99999))
    ob = create_object(self, OAIToken, id)
    if not kwargs['token_args'].has_key('id'):
            kwargs['token_args']['id'] = id
    process_form(ob, IOAIToken, kwargs)
    ob.expiration = kwargs['token_args']['expirationDate']
    return ob

class OAIToken(SimpleItem, Implicit):
    """ """
    meta_type = 'Zope OAI Resumption Token'
    manage_options= ({'label': 'Contents', 'action': 'index_html'},)
