""" Products Info
"""
try:
    # Naaya context
    from Products.Naaya.interfaces import INySite as ISite
except ImportError:
    # Other context
    from zope.interface import Interface as ISite
