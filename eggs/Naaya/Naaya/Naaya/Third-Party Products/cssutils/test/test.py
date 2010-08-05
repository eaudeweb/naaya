"""
the start module for cssutils unittests
"""
__version__ = '0.51'

import unittest

from test_lexer import *
from test_cssparser import *
from test_cssbuilder import *

from test_cssstylesheet import *

from test_csscharsetrule import *
from test_cssimportrule import *
from test_cssfontfacerule import *
from test_csspagerule import *

from test_cssmediarule import *
from test_medialist import *

from test_cssrule import *
from test_cssrulelist import *
from test_cssstylerule import *
from test_cssstyledeclaration import *

from test_cssproperties import *

from test_cssvalue import *
from test_cssprimitivevalue import *
from test_cssvaluelist import *
from test_cssvalue_other import * # Counter, Rect, RGB

print "starting unittests for cssutils"
unittest.main()
