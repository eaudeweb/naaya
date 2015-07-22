#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "GeoMapTool"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA). Portions created by Eau de Web are Copyright (C)
#2007 by European Environment Agency. All Rights Reserved.
""" Utilities package strictly related to EditorTool
@author: Cristian Romanescu
@version: 1.0
@organization: Eau De Web
@since: Nov 19, 2009
"""
def strip_unit(val):
    """ Strip units from a CSS value
    `value` Some value like: 12px, 13em etc.
    Return value without CSS units
    Reference: http://www.w3schools.com/css/css_units.asp
    """
    if val and len(val) >= 1 and val[-1:] == '%':
        return val[0:-1]
    if val and len(val) >= 2 and \
            val[-2:] in ('mm', 'in', 'em', 'ex', 'px', 'pt', 'pc'):
        return val[0:-2]
    return val


def parse_css_margin(margin):
    """ Parse css 'margin' property (margin: top[px] rght[px] bottom[px] left[px])
    Parameters:
        `val` 
            property. Something like: 2px 5em
    Return an array of 4 elements initialized with values (or [0,0,0,0] if
    not correctly initialized or invalid. They are the margin width.
    Reference: http://www.w3schools.com/css/css_margin.asp
    """
    ret = [0,0,0,0]
    if margin:
        parts = margin.split(' ')
        clean = [strip_unit(x) for x in parts]
        if len(parts) == 4:
            ret = clean
        if len(parts) == 3:
            ret = [clean[0], clean[1], clean[2], clean[1]]
        if len(parts) == 2:
            ret = [clean[0], clean[1], clean[0], clean[1]]
        if len(parts) == 1:
            ret = [clean[0], clean[0], clean[0], clean[0]]
    return ret


def parse_css_border_width(border):
    """ Parse the CSS 'border' property. border allows all attributes in one.
    Parameters:
        `border` 
            Border property such as: black 1px solid
    Returns width of the border as number
    Reference: http://www.w3schools.com/css/css_border.asp
    """
    ret = ''
    if border:
        parts = border.split(' ')
        predef = ('thin', 'medium', 'thick')
        nos = [str(x) for x in range(0, 9)]
        for part in parts:
            #Detect in which part the size is located
            if len(part) >= 1 and part[0] in (nos):
                return strip_unit(part)
        for part in parts:
            if part in predef:
                return part
    return ret

#Unit testing
import unittest
from unittest import TestCase

class FileTest(TestCase):

    def test_strip_unit(self):
        self.assertEqual('23', strip_unit('23%'))
        self.assertEqual('23', strip_unit('23px'))
        self.assertEqual('1', strip_unit('1%'))
        self.assertEqual('0', strip_unit('0mm'))
        self.assertEqual(None, strip_unit(None))


    def test_parse_css_margin(self):
        self.assertEqual(['1','2','3','4'], parse_css_margin('1% 2em 3px 4'))
        self.assertEqual(['1','2','3','2'], parse_css_margin('1% 2em 3px'))
        self.assertEqual(['1','2','1','2'], parse_css_margin('1% 2em'))
        self.assertEqual(['1','1','1','1'], parse_css_margin('1%'))


    def test_parse_css_border_width(self):
        self.assertEqual('1', parse_css_border_width('1px solid red'))
        self.assertEqual('2', parse_css_border_width('solid red 2em'))
        self.assertEqual('thin', parse_css_border_width('solid red thin'))
        self.assertEqual('medium', parse_css_border_width('solid medium red'))
        self.assertEqual('thick', parse_css_border_width('solid thick #F0F0F0'))
        self.assertEqual('2', parse_css_border_width('#C0C0C0 2mm blue'))

if __name__ == "__main__":
    unittest.main()
