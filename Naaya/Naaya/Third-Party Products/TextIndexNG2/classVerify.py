###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
wrapper around the verify function of the interface package because
Jim changed the API from Zope 2.5 to Zope 2.6

$Id: classVerify.py,v 1.2 2003/07/09 17:33:47 ajung Exp $
"""

try:
    from Interface.verify import verify_class_implementation as verifyClass
except:
    from Interface.Verify import verifyClass, verifyObject

