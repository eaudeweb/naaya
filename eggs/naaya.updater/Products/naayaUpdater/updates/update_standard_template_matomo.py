from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.updates.utils import get_standard_template


class UpdateMatomo(UpdateScript):
    """ """
    title = 'Add matomo script to standard_template'
    creation_date = 'Sep 25, 2018'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['HIGH']
    description = ('Add matomo script to standard_template')

    def _update(self, portal):
        self.log.debug('Updating standard_template')
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        matomo = '''<!-- Matomo -->
        <script type="text/javascript">
          var _paq = _paq || [];
          /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
          _paq.push(['trackPageView']);
          _paq.push(['enableLinkTracking']);
          (function() {
            var u="https://matomo.eea.europa.eu/";
            _paq.push(['setTrackerUrl', u+'piwik.php']);
            _paq.push(['setSiteId', '16']);
            var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
            g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'piwik.js'; s.parentNode.insertBefore(g,s);
          })();
        </script>
        <noscript>
        <!-- Matomo Image Tracker-->
        <img src="https://matomo.eea.europa.eu/piwik.php?idsite=16&amp;rec=1"
            tyle="border:0" alt="" />
        <!-- End Matomo Image Tracker -->
        </noscript>
        <!-- End Matomo Code -->
        </body>'''
        if matomo not in tal:
            tal = tal.replace('</body>', matomo)
            standard_template.write(tal)
            self.log.debug(
                'matomo code added to standard template')
        else:
            self.log.debug('matomo code already in standard_template')
        return True
