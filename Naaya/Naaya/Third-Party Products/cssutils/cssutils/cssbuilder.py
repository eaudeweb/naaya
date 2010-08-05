"""
classes to support building a CSS Cascading StyleSheet.

Usage:
    from cssutils.cssbuilder import *
    # init CSSStylesheet
    css = StyleSheet()

    # build a rule
    r = StyleRule()
    r.addSelector('body')
    r.addSelector('b') # a second one
    d = StyleDeclaration()
    d.setProperty('color', 'red') # old addProperty is DEPRECATED
    r.setStyleDeclaration(d)

    # build @media Rule
    mr = MediaRule(' print,   tv ')
    d = StyleDeclaration()
    d.setProperty('color', '#000')
    r = StyleRule('body', d)
    mr.addRule(r)

    # compose stylesheet
    css.addComment('basic styles')
    css.addComment('styles for print or tv')
    css.addRule(mr)
    css.insertRule(r, 1)

    # output
    css.pprint(2)
"""
__version__ = '0.51'

import xml.dom

from cssutils import *

from cssstylesheet import *

from cssrule import *
from csscharsetrule import *
from cssfontfacerule import *
from cssimportrule import *
from csspagerule import *

from cssmediarule import *
from medialist import *

from cssstylerule import *

from cssstyledeclaration import *
from cssvalue import *


if __name__ == '__main__':
    import sys
    try:
        if 'debug' == sys.argv[1]:
            from cssutils.cssbuilder import *
            # init CSSStylesheet
            css = StyleSheet()

            # build a rule
            r = StyleRule()
            r.addSelector('body')
            r.addSelector('b') # a second one
            d = StyleDeclaration()
            d.setProperty('color', 'red') # old addProperty is DEPRECATED
            r.setStyleDeclaration(d)

            # build @media Rule
            mr = MediaRule(' print,   tv ')
            d = StyleDeclaration()
            d.setProperty('color', '#000')
            r = StyleRule('body', d)
            mr.addRule(r)

            # compose stylesheet
            css.addComment('basic styles')
            css.addComment('styles for print or tv')
            css.addRule(mr)
            css.insertRule(r, 1)

            # output
            css.pprint(2)
    except:
        pass