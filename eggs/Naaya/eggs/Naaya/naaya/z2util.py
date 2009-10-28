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
naaya.z2util - utilities to make Zope 2 a friendlier place
"""

from AccessControl import ClassSecurityInfo as Z2_ClassSecurityInfo

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

class ClassSecurityInfo(Z2_ClassSecurityInfo):
    def public(self, func):
        self.declarePublic(func.func_name)
        return func

    def protected(self, permission):
        def decorator(func):
            self.declareProtected(permission, func.func_name)
            return func
        return decorator

    def private(self, func):
        self.declarePrivate(func.func_name)
        return func
