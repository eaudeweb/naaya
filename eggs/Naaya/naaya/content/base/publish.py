# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import mimeparse

from zope.component import adapts
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

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
                return INyRdfView(self.context)

            # add other custom index views here

        return self.fallback(request, name)

def client_wants_rdf(request):
    accept = request.HTTP_ACCEPT or 'text/html'
    known_types = ['application/rdf+xml', 'text/html']
    try:
        mime_type = mimeparse.best_match(known_types, accept)
    except:
        # something went wrong; assume client doesn't want RDF
        return False

    if mime_type == 'application/rdf+xml':
        return True

    if request.get('format', None) == 'rdf':
        return True

    return False

class DefaultRdfView(object):
    def __init__(self, context):
        self.context = context

    basic_rdf = PageTemplateFile('zpt/basic_rdf', globals())
    def __call__(self, REQUEST):
        REQUEST.RESPONSE.setHeader('Content-Type', "application/rdf+xml")
        return self.basic_rdf.__of__(self.context)(REQUEST)
