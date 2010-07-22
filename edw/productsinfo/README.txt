Products Info
=============
This package provides a zope view called ''products.info'' that exports all
installed products information in your zope2 application as JSON

    >>> self.login('admin')
    >>> view = self.portal.restrictedTraverse('products.info')
    >>> view()
    '[{"version": ..., "name": ...}, ...]'

Or you can access it using zope.components

    >>> from zope.component import getMultiAdapter
    >>> view = getMultiAdapter((self.portal, self.portal.REQUEST), name=u'products.info')
    >>> view()
    '[{"version": ..., "name": ...}, ...]'

Load json

    >>> import simplejson
    >>> simplejson.loads(view())
    [{'version': ..., 'name': ...}, ...]
