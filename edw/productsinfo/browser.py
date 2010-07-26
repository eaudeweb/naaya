""" Browser Views
"""
import simplejson as json
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import NotFound

class View(BrowserPage):
    """Provides information about installed products
    in Json format, required manager authentication
    """

    @property
    def token(self):
        """ Authentication token
        """
        return getattr(self.context, 'edw-productsinfo-key', None)

    def publishTraverse(self, request, name):
        token = self.token
        if not token:
            return json.dumps({
                'error': 'Unauthorized: Token not set on this instance'
            })

        if self.token != name:
            return json.dumps({
                'error': 'Invalid authentication token'
            })

        products=[]
        products_folder = self.context.Control_Panel.Products
        for product_name in products_folder.objectIds():
            product = products_folder._getOb(product_name, None)
            if(product is not None and product.thisIsAnInstalledProduct == 1):
                products.append({
                    'name': product.id,
                    'version': product.version
                })
        return json.dumps(products)

    def __call__(self, **kwargs):
        raise NotFound(self.context, 'products.info', self.request)
