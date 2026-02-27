from Products.naayaUpdater.updates import UpdateScript

public_key = '6Le-Z8kSAAAAAEVXFw-W-IbOCt1o9lZ-4GqEQgSR'
private_key = '6Le-Z8kSAAAAAEp1SHv5uBpcyY46JaPiY7dzD8B0'

class UpdateRecaptchaKeys(UpdateScript):
    """ """
    title="Set each reCAPTCHA key for CHMBE with unique value"
    authors=["Andrei Laza"]
    creation_date = 'Oct 24, 2011'
    description="set public key '%s' and private key '%s'" % (
            public_key, private_key)

    def _update(self, portal):
        if (portal.recaptcha_public_key == public_key
                and portal.recaptcha_private_key == private_key):
            self.log.debug('No need to update')
            return True

        portal.recaptcha_public_key = public_key
        portal.recaptcha_private_key = private_key
        self.log.debug('recaptcha keys are set')
        return True
