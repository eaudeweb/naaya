from App.config import getConfiguration
from Products.Five.browser import BrowserView
from naaya.component import bundles
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaBase import akismet

tmpl = NaayaPageTemplateFile('zpt/site_admin_api_keys', globals(), 'admin_api_keys')

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

def AdminAPIKeysStatus(context, request):
    """
    Check if API keys exists and are valid
    """
    conf = getConfiguration()

    #Akismet
    api_keys = {
        'akismet':{
            'key': '',
            'valid': False
        }
    }

    akismet_api_key = getattr(conf, 'environment', {}).get('AKISMET_API_KEY', '')
    valid = False
    if akismet_api_key:
        valid = akismet.verify_key(akismet_api_key, context.getSitePath())

    api_keys['akismet'] = {
        'key': akismet_api_key,
        'valid': valid
    }

    #Google Analytics
    ga_id = getattr(context.portal_statistics, 'ga_id', '')
    valid = False
    if ga_id == '':
        ga_id = getattr(conf, 'environment', {}).get('GA_ID', '')

    if ga_id:
        valid = True

    api_keys['ga_id'] = {
        'key': ga_id,
        'valid': valid
    }

    #reCaptcha
    recaptcha_private_key = getattr(context, 'recaptcha_private_key', '')
    valid = False
    if recaptcha_private_key:
        valid = True

    api_keys['recaptcha_private_key'] = {
        'key': recaptcha_private_key,
        'valid': valid
    }

    recaptcha_public_key = getattr(context, 'recaptcha_public_key', '')
    valid = False
    if recaptcha_public_key:
        valid = True

    api_keys['recaptcha_public_key'] = {
        'key': recaptcha_public_key,
        'valid': valid
    }

    options = {
        'here': context,
        'api_keys': api_keys,
    }

    return tmpl.__of__(context)(**options)
