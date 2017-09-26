""" Products Info
"""
try:
    # Naaya context
    from Products.Naaya.interfaces import INySite as ISite
except ImportError:
    # Other context
    from zope.interface import Interface as ISite

import md5
import logging
import transaction
from datetime import datetime
logger = logging.getLogger('edw.productsinfo')

def initialize(context):
    """ """
    #Add private key
    app = context._ProductContext__app

    if hasattr(app, 'edw-productsinfo-key'):
        return

    now = datetime.now()
    now = now.isoformat()
    logger.info('Added property edw-productsinfo-key on zope instance')
    app.manage_addProperty(id='edw-productsinfo-key', type='string',
                           value=md5.new(now).hexdigest())
    transaction.commit()
