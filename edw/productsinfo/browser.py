""" Browser Views
"""
import Zope2
import simplejson as json
from Products.Five.browser import BrowserView

class View(BrowserView):
    """Provides information about installed products
    in Json format, required manager authentication
    """
    def __call__(self, **kwargs):
        # check for installed products
        products=[]
        products_folder = Zope2.app().Control_Panel.Products
        for product_name in products_folder.objectIds():
            product = products_folder._getOb(product_name, None)
            if(product is not None and product.thisIsAnInstalledProduct == 1):
                products.append({
                    'name': product.id,
                    'version': product.version
                })
        return json.dumps(products)
