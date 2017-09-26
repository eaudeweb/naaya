""" Browser Views
"""
try:
    import simplejson as json
except ImportError:
    import json
import Zope2
from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
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

    def provide_json(self):
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
        return self.provide_json()

    def __call__(self, **kwargs):
        raise NotFound(self.context, 'products.info', self.request)

class Portals(Info):
    """ Provides information about portals
    """
    def provide_json(self):
        root = Zope2.app()
        portals = []
        for (id, obj) in root.objectItems():
            # if it has a valid error_log, then it should be a portal (website)
            try:
                erlog = obj._getOb('error_log', None)
                if erlog is not None and isinstance(erlog, SiteErrorLog):
                    portals.append(obj.getPhysicalPath()[1])
            except AttributeError:
                continue
        return json.dumps(portals)

class Errors(Info):
    """ Provides portal errors_log
    """
    def provide_json(self):
        er = self.context._getOb('error_log', None)
        errors = []
        # double check object type, although 'error_log' is a zope sine-qua-non
        if er is not None and isinstance(er, SiteErrorLog):
            er_list = er.getLogEntries()
            for err in er_list:
                errors.append({'id': err['id'], 
                               'error_name': err['value'],
                               'error_type': err['type'],
                               'date': err['time'],
                               'traceback': err['tb_text'],
                               'url': er.getPhysicalPath()[2] + '/showEntry?id='
                               + err['id']})
        return json.dumps(errors)
