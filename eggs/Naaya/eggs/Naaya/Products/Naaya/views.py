from Products.Five.browser import BrowserView
from naaya.component import bundles


class SetBundleView(BrowserView):
    """ Change a site's bundle from ZMI """

    def __call__(self, *args, **kw):
        self.request.SESSION.set('message', "")
        if 'bundle' in self.request:
            if self.request['bundle']:
                self.set_bundle(self.request['bundle'])
                self.request.SESSION.set('message', "Success!")
            else:
                self.request.SESSION.set('message',
                        "Bundle name cannot be empty!")
        return super(SetBundleView, self).__call__(*args, **kw)

    def set_bundle(self, bundle_name):
        self.context.getSite().set_bundle(bundles.get(bundle_name))

    def get_bundle(self):
        return self.context.getSite().get_bundle().__name__
