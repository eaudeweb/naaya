#Copyright (c) 2005, the Lawrence Journal-World
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification,
#are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Django nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

class ObjectPaginator:
    """
    This class makes pagination easy. Feed it a QuerySet or list, plus the number
    of objects you want on each page. Then read the hits and pages properties to
    see how many pages it involves. Call get_page with a page number (starting
    at 0) to get back a list of objects for that page.

    Finally, check if a page number has a next/prev page using
    has_next_page(page_number) and has_previous_page(page_number).
    
    Use orphans to avoid small final pages. For example:
    13 records, num_per_page=10, orphans=2 --> pages==2, len(self.get_page(0))==10
    12 records, num_per_page=10, orphans=2 --> pages==1, len(self.get_page(0))==12
    """

    def __init__(self, query_set, num_per_page, orphans=0):
        self.query_set = query_set
        self.num_per_page = num_per_page
        self.orphans = orphans
        self._hits = self._pages = None
        self._page_range = None

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    def validate_page_number(self, page_number):
        try:
            page_number = int(page_number)
        except:
            page_number = 0
        if page_number < 0 or page_number > self.pages - 1:
            page_number = 0
        return page_number

    def get_page(self, page_number):
        page_number = self.validate_page_number(page_number)
        bottom = page_number * self.num_per_page
        top = bottom + self.num_per_page
        if top + self.orphans >= self.hits:
            top = self.hits
        return self.query_set[bottom:top]

    def has_next_page(self, page_number):
        "Does page $page_number have a 'next' page?"
        return page_number < self.pages - 1

    def has_previous_page(self, page_number):
        return page_number > 0

    def first_on_page(self, page_number):
        """
        Returns the 1-based index of the first object on the given page,
        relative to total objects found (hits).
        """
        page_number = self.validate_page_number(page_number)
        return (self.num_per_page * page_number) + 1

    def last_on_page(self, page_number):
        """
        Returns the 1-based index of the last object on the given page,
        relative to total objects found (hits).
        """
        page_number = self.validate_page_number(page_number)
        page_number += 1   # 1-base
        if page_number == self.pages:
            return self.hits
        return page_number * self.num_per_page

    def _get_hits(self):
        if self._hits is None:
            # Try .count() or fall back to len().
            try:
                self._hits = int(self.query_set.count())
            except (AttributeError, TypeError, ValueError):
                # AttributeError if query_set has no object count.
                # TypeError if query_set.count() required arguments.
                # ValueError if int() fails.
                self._hits = len(self.query_set)
        return self._hits

    def _get_pages(self):
        if self._pages is None:
            hits = (self.hits - 1 - self.orphans)
            if hits < 1:
                hits = 0
            self._pages = hits // self.num_per_page + 1
        return self._pages

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within 
        a template for loop.
        """
        if self._page_range is None:
            self._page_range = range(1, self._pages + 1)
        return self._page_range

    hits = property(_get_hits)
    pages = property(_get_pages)
    page_range = property(_get_page_range)

InitializeClass(ObjectPaginator)