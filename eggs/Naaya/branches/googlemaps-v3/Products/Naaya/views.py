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
        'title': 'Akismet',
        'description': 'Filters comments and track-back spam',
        'key': akismet_api_key,
        'valid': valid,
        'change_link': None
    }

    google_client_id = getattr(conf, 'environment', {}).get('GOOGLE_AUTH_CLIENT_ID', '')
    valid = False
    if google_client_id:
        valid = True

    api_keys['google_client_id'] = {
        'title': 'Google Authentication Client ID',
        'description': 'Google Authentication Client ID',
        'key': None,
        'valid': valid,
        'change_link': None
    }

    google_client_secret = getattr(conf, 'environment', {}).get('GOOGLE_AUTH_CLIENT_SECRET', '')
    valid = False
    if google_client_secret:
        valid = True

    api_keys['google_client_secret'] = {
        'title': 'Google Authentication Client Secret Key',
        'description': 'Google Authentication Client Secret Key',
        'key': None,
        'valid': valid,
        'change_link': None
    }

    master_ga_id = getattr(conf, 'environment', {}).get('GA_ID', '')
    valid = False
    if master_ga_id:
        valid = True

    api_keys['master_ga_id'] = {
        'title': 'Google Analytics primary tracking code',
        'description': 'The GA web property of the master profile (the profile of the top-level domain)',
        'key': master_ga_id,
        'valid': valid,
        'change_link': None
    }

    ga_domain_name = getattr(conf, 'environment', {}).get('GA_DOMAIN_NAME', '')
    valid = False
    if ga_domain_name:
        valid = True

    api_keys['ga_domain_name'] = {
        'title': 'Google Analytics domain name',
        'description': 'Sets the domain name to the top-level domain for '
                       'the portal',
        'key': ga_domain_name,
        'valid': valid,
        'change_link': None
    }

    #Google Analytics
    ga_id = getattr(context.portal_statistics, 'ga_id', '')
    valid = False
    if ga_id:
        valid = True

    api_keys['ga_id'] = {
        'title': 'Google Analytics portal tracking code',
        'description': 'Allows Google to access your website traffic data and saves data in portal profile of GA.',
        'key': ga_id,
        'valid': valid,
        'change_link': '/portal_statistics/admin_verify'
    }

    #reCaptcha
    recaptcha_private_key = context.get_recaptcha_private_key()
    valid = False
    if recaptcha_private_key:
        valid = True

    api_keys['recaptcha_private_key'] = {
        'title': 'reCaptcha private key',
        'description': 'reCaptcha private key for CAPTCHA verification',
        'key': recaptcha_private_key,
        'valid': valid,
        'change_link': '/admin_properties_html'
    }

    recaptcha_public_key = context.get_recaptcha_public_key()
    valid = False
    if recaptcha_public_key:
        valid = True

    api_keys['recaptcha_public_key'] = {
        'title': 'reCaptcha public key',
        'description': 'reCaptcha public key for CAPTCHA verification',
        'key': recaptcha_public_key,
        'valid': valid,
        'change_link': '/admin_properties_html'
    }

    options = {
        'here': context,
        'api_keys': api_keys,
    }

    return tmpl.__of__(context)(**options)
