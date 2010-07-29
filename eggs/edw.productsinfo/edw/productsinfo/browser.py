""" Browser Views
"""
import simplejson as json
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import NotFound

class Info(BrowserPage):
    """Provides information about installed products
    in Json format, required manager authentication
    """
    def check_token(self, token):
        """ Authentication token check
        """
        key = getattr(self.context, 'edw-productsinfo-key', None)
        if not key:
            return {
                'error': 'Unauthorized: Token not set on this instance'
            }

        if key != token:
            return {
                'error': 'Invalid authentication token'
            }
        return {}


    def json(self):
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

    def publishTraverse(self, request, name):
        error = self.check_token(name)
        if error:
            return json.dumps(error)
        return self.json()

    def __call__(self, **kwargs):
        raise NotFound(self.context, 'products.info', self.request)

class Portals(Info):
    """ Provides information about portals
    """
    def json(self):
        return json.dumps({'error': 'Not implemented error'})

class Errors(Info):
    """ Provides portal errors_log
    """
    def json(self):
        return json.dumps({'error': 'Not implemented error'})
