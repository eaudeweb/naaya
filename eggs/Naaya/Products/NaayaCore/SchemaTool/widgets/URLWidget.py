from urlparse import urlparse
import re

from Globals import InitializeClass

from StringWidget import StringWidget
from Widget import manage_addWidget

def addURLWidget(container, id="", title="URL Widget", REQUEST=None,
        **kwargs):
    return manage_addWidget(URLWidget, container, id, title, REQUEST, **kwargs)

class URLWidget(StringWidget):
    meta_type = "Naaya Schema URL Widget"
    meta_label = "Text interpreted as URL"
    meta_description = "Tries to parse the input string to give an accurate URL"

    _constructors = (addURLWidget,)

    def parseFormData(self, value):
        """Get URL from form value"""
        return convert_string_to_URL(value)

InitializeClass(URLWidget)

def convert_string_to_URL(value):
    scheme, netloc, path, params, query, fragment = urlparse(value)
    if netloc: # absolute url: has network location
        return value

    if value.startswith('www.'):
        # convert misstyped absolute url
        return 'http://' + value

    return value
