from Acquisition import Implicit
from OFS.SimpleItem import SimpleItem

from utils import create_object, process_form

from interfaces import IOAIToken

def manage_addOAIToken(self, id, **kwargs):
    """ """
    ob = create_object(self, OAIToken, id)
    if not kwargs['token_args'].has_key('id'):
            kwargs['token_args']['id'] = id
    process_form(ob, IOAIToken, kwargs)
    ob.expiration = kwargs['token_args']['expirationDate']

class OAIToken(SimpleItem, Implicit):
    """ """
    meta_type = 'Zope OAI Resumption Token'
    manage_options= ({'label': 'Contents', 'action': 'index_html'},)

    def __getattr__(self, name):
        if getattr(self, name) is not None:
            return getattr(self, name)
        else:
            return self.token_args.get(name, self.request_args.get(name))
