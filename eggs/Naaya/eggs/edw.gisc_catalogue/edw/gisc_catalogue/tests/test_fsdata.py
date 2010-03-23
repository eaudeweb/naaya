import unittest
import tempfile
import shutil
from os import path
import datetime

import rdflib

from edw.gisc_catalogue.fsdata import FilesystemDatasource

def read_fixture(file_name):
    f = open(path.join(path.dirname(__file__), file_name), 'rb')
    file_data = f.read()
    f.close()
    return file_data

ns = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dcmi': 'http://purl.org/dc/dcmitype/',
    'dcterms': 'http://purl.org/dc/terms/',
    'test': 'http://test.edw.ro/gisc_catalogue/',
    'gisc': 'http://gisc.ew.eea.europa.eu/rdf/'
}

class FsDataTest(unittest.TestCase):
    def setUp(self):
        self.datapath = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.datapath)

    def add_file(self, file_name, file_data):
        f = open(path.join(self.datapath, file_name), 'wb')
        f.write(file_data)
        f.close()

    def test_parse_rdf(self):
        expected_triples = [
            (rdflib.URIRef(ns['test']+'eea/AirBaseData'),
             rdflib.URIRef(ns['rdf']+'type'),
             rdflib.URIRef(ns['gisc']+'Product')),

            (rdflib.URIRef(ns['test']+'eea/AirBaseData'),
             rdflib.URIRef(ns['dcterms']+'title'),
             rdflib.Literal("Eionet air quality database")),

            (rdflib.URIRef(ns['test']+'eea/AirBaseStations'),
             rdflib.URIRef(ns['rdf']+'type'),
             rdflib.URIRef(ns['gisc']+'Dataset')),
        ]

        self.add_file('airbase.n3', read_fixture('airbase.n3'))
        ds = FilesystemDatasource(self.datapath)
        graph = ds._read_data()
        for triple in expected_triples:
            self.assertTrue(triple in graph,
                            'triple missing: %r' % (triple,))

    def test_list_organizations(self):
        self.add_file('airbase.n3', read_fixture('airbase.n3'))
        ds = FilesystemDatasource(self.datapath)
        orgs = list(ds.list_organizations())
        self.assertEqual(len(orgs), 1)
        org_eea = orgs[0]
        self.assertEqual(org_eea.name, "European Environment Agency")
        self.assertEqual(org_eea.uri, ns['test']+"eea/EEA")
        self.assertEqual(org_eea.homepage, "http://www.eea.europa.eu/")

    def test_get_organization(self):
        self.add_file('airbase.n3', read_fixture('airbase.n3'))
        ds = FilesystemDatasource(self.datapath)
        org_eea = ds.get_organization(ns['test']+"eea/EEA")
        self.assertEqual(org_eea.name, "European Environment Agency")
        self.assertEqual(org_eea.uri, ns['test']+"eea/EEA")
        self.assertEqual(org_eea.homepage, "http://www.eea.europa.eu/")

    def test_list_all_products(self):
        self.add_file('airbase.n3', read_fixture('airbase.n3'))
        self.add_file('naval.n3', read_fixture('naval.n3'))
        ds = FilesystemDatasource(self.datapath)
        products = dict( (prod.uri, prod) for prod in ds.list_products() )
        self.assertEqual(len(products), 3)
        self.assertEqual(set(products.keys()), set([
            ns['test']+'eea/AirBaseData',
            ns['test']+'naval/ShipRegistry',
            ns['test']+'naval/ClientService']))

        ship_registry = products[ns['test']+'naval/ShipRegistry']
        self.assertEqual(ship_registry.title, "Ships owned by the company")
        self.assertEqual(ship_registry.description,
                         "Info about FirstNavalCompany's ships.")
        self.assertEqual(ship_registry.organization_uri,
                         ns['test']+'naval/FirstNavalCompany')
        self.assertTrue(ship_registry.homepage is None)
        self.assertTrue(ship_registry.modified is None)

        airbase = products[ns['test']+'eea/AirBaseData']
        self.assertTrue(isinstance(airbase.modified, datetime.date))
        self.assertEqual(airbase.modified, datetime.date(2010, 3, 4))
        self.assertEqual(airbase.homepage,
                         "http://air-climate.eionet.europa.eu/"
                            "databases/airbase/")

    def test_list_products_by_organization(self):
        self.add_file('airbase.n3', read_fixture('airbase.n3'))
        self.add_file('naval.n3', read_fixture('naval.n3'))
        ds = FilesystemDatasource(self.datapath)

        def products_of(org_uri):
            return set(prod.uri for prod in
                       ds.list_products(organization=org_uri))

        self.assertEqual(products_of(ns['test']+'eea/EEA'),
                         set([ns['test']+'eea/AirBaseData']))
        self.assertEqual(products_of(ns['test']+'naval/FirstNavalCompany'),
                         set([ns['test']+'naval/ShipRegistry',
                              ns['test']+'naval/ClientService']))
