from unittest import TestCase

class Staging(TestCase):
    def portals(self):
        return self.app.objectValues('Groupware site')

class TestAnonymous(Staging):
    """ Test anonymous stuff """
    #Interest groups that you can access
    membership_sites = [
        'AMP 2011 Consultation',
        'EEA general documents',
        'ETC BD Consortium',
        'ETC/ACM Consortium',
        'NRC FLIS Interest Group',
        'NRC Maritime Interest Group',
        'NRC Nature and Biodiversity Interest Group',
    ]
    restricted_sites = [
        'Author team of the 2012 EEA et al. report on climate change impacts, vulnerability, and adaptation',
        'EEA West Balkans cooperation Interest Group',
        'EMAS outreach project Interest Group',
        'ETC/CCA Consortium',
        'Eionet Forum on SCP including resource use and waste',
        'NFP / Eionet Interest Group',
        'NRC Agriculture and Forests Interest Group',
        'NRC Land Cover Interest Group',
        'UNEP_WATER',
    ]
    archived_sites = [
        'DIS-MED',
        'EU 98 Report',
        'Eionet NMC',
        'GEMET',
        'IRENA',
    ]
    def test_portal_links(self):
        """ Check if links are all there """
        txt = self.selenium.get_text
        self.selenium.open('/')

        xpath_selector = "//ul[@class='ig_listing'][%s]/li[%s]/a"
        for i, site in enumerate(self.membership_sites):
            assert site in txt(xpath_selector % (1, str(i+1))), xpath_selector % (1, str(i+1))

        for i, site in enumerate(self.restricted_sites):
            assert site in txt(xpath_selector % (2, str(i+1))), xpath_selector % (2, str(i+1))

        for i, site in enumerate(self.archived_sites):
            assert site in txt(xpath_selector % (3, str(i+1))), xpath_selector % (3, str(i+1))

    def test_restricted_portals(self):
        """ Some portals are restricted. Some are accessible. """
        for portal in self.portals():
            self.selenium.open(portal.absolute_url(1))
            self.selenium.wait_for_page_to_load(5000)

            self.assertEqual(portal.portal_is_restricted,
                    self.selenium.is_element_present("//h1[text()='Login']"))
