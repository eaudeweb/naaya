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

"""
naaya.core.zope2util - utilities to make Zope 2 a friendlier place
"""

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass
from AccessControl.Permissions import view
from zope.pagetemplate.pagetemplatefile import PageTemplateFile


def redirect_to(tmpl):
    """
    Generate a simple view that redirects to the specified URL.

    For example, this declaration:
    >>> the_old_page = redirect_to('%(self_url)s/the_new_page')

    is equivalent with:
    >>> def the_new_page(self, REQUEST):
    >>>     ''' perform redirect '''
    >>>     REQUEST.RESPONSE.redirect(self.absolute_url() + '/the_new_page')

    """
    def redirect(self, REQUEST):
        """ automatic redirect """
        url = tmpl % {
            'self_url': self.absolute_url(),
        }
        REQUEST.RESPONSE.redirect(url)
    return redirect

class NaayaTemplateHelper(Implicit, object):
    security = ClassSecurityInfo()

    def get_site(self):
        return self.aq_parent

    _button_form = PageTemplateFile('zpt/button_form.zpt', globals())
    security.declarePublic('button_form')
    def button_form(self, **kwargs):
        return self._button_form(**kwargs)

InitializeClass(NaayaTemplateHelper)


class CaptureTraverse(Implicit):
    """
    Capture any request path and invoke a callback.

    CaptureTraverse is useful when we need to capture arbitrary request
    paths. If our object is published at `http://example.com/my/object`,
    and we expect requests at `http://example.com/my/object/magic/a/b/c`,
    then we can use CaptureTraverse like so::

      >>> def handle_magic(context, path, REQUEST):
      ...     return ('the page! path=%r, url=%r' %
                      (path, context.absolute_url()))
      >>> class MyObject(SimpleItem):
      ...     # implementation of MyObject
      ...     # ...
      ...
      ...     magic = CaptureTraverse(handle_magic)

    GET requests for `http://example.com/my/object/magic/a/b/c` will
    receive the following response::

      the page! path=('a', 'b', 'c'), url='http://example.com/my/object'

    """

    security = ClassSecurityInfo()

    def __init__(self, callback, path=tuple(), context=None):
        self.callback = callback
        self.path = path
        self.context = context

    def __bobo_traverse__(self, REQUEST, name):
        new_path = self.path + (name,)
        context = self.context or (self.aq_parent,)
        return CaptureTraverse(self.callback, new_path, context).__of__(self)

    def __call__(self, REQUEST):
        assert self.path[-1] == 'index_html'
        return self.callback(self.context[0], self.path[:-1], REQUEST)
