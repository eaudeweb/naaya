"""
cssutils setup

install with
    >python setup.py install
"""
__version__ = '0.51'

import sys

major, minor = sys.version_info[:2]
if not (major >= 2 and minor >= 3):
    print
    sys.exit('Cannot install, cssutils need at least Python 2.3.')


from distutils.core import setup

_long = '''A Python package to parse and build CSS Cascading Style Sheets.
Partly implements the DOM Level 2 CSS interfaces.
Additional some cssutils only convenience and (hopefully) more pythonic
methods are integrated.

Cssutils starting point was normalization and pretty printing of given CSS
files to be able to compare them more easily. It then developed into
something similar what the DOM CSS interfaces would do anyway, so it went
from there...
Additionally a focus should be on the various CSS hacks that were developed
to overcome several browser CSS incompabilities. Cssutils should at least
be able to preserve these hacks. 
'''
setup(
      author='Christof Hoeke',
      author_email='c@cthedot.de',
      description='A CSS Cascading Style Sheets library for Python.',
      long_description=_long,
      keywords = 'CSS, Cascading Style Sheets, CSSParser, DOM Level 2 CSS',
      license = 'http://cthedot.de/cssutils/license.html',
      name = 'cssutils',
      url = 'http://cthedot.de/cssutils/',
      version = __version__,
      packages = ['cssutils'],
      data_files=[('', ['LICENSE.txt'])]
      )