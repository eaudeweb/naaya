import urllib
import mimeparse

from zope.component import adapts
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit

from naaya.content.base.interfaces import INyContentObject
from naaya.content.base.interfaces import INyRdfView

class NyContentPublishTraverse(DefaultPublishTraverse):
    adapts(INyContentObject, IRequest)

    def fallback(self, request, name):
        sup = super(NyContentPublishTraverse, self)
        return sup.publishTraverse(request, name)

    def publishTraverse(self, request, name):
        if name == 'index_html':
            # we are asked for the object's index page
            if client_wants_rdf(request):
                view = INyRdfView(self.context)
                # view needs to support acquisition (hello, Zope2 security!)
                return view.__of__(self.context)

            # add other custom index views here

        return self.fallback(request, name)

def client_wants_rdf(request):
    if request.get('format', None) == 'rdf':
        return True

    accept = request.HTTP_ACCEPT or 'text/html'
    known_types = ['application/rdf+xml', 'text/html']
    try:
        mime_type = mimeparse.best_match(known_types, accept)
    except:
        pass # something went wrong; assume content negotiation failed
    else:
        if mime_type == 'application/rdf+xml':
            return True

    return False

def object_type_uri(obj):
    if obj.meta_type.startswith('Naaya '):
        type_name = obj.meta_type[6:]
    else:
        type_name = 'other'

    return 'http://naaya.eaudeweb.ro/rdf/type/' + urllib.quote(type_name, '')

class DefaultRdfView(Implicit):
    def __init__(self, context):
        self.context = context

    basic_rdf = PageTemplateFile('zpt/basic_rdf', globals())

    def __call__(self, REQUEST):
        REQUEST.RESPONSE.setHeader('Content-Type', "application/rdf+xml")
        options = {'object_type_uri': object_type_uri(self.context)}
        return self.basic_rdf.__of__(self.context)(REQUEST, **options)
