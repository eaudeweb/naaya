import os
from os import path
import datetime

import rdflib
from rdflib.Graph import Graph

ns = {
    'dc': rdflib.Namespace("http://purl.org/dc/elements/1.1/"),
    'rdf': rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    'rdfs': rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#"),
    'owl': rdflib.Namespace("http://www.w3.org/2002/07/owl#"),
    'xsd': rdflib.Namespace("http://www.w3.org/2001/XMLSchema#"),
    'foaf': rdflib.Namespace("http://xmlns.com/foaf/0.1/"),
    'dcterms': rdflib.Namespace("http://purl.org/dc/terms/"),
    'dcmi': rdflib.Namespace("http://purl.org/dc/dcmitype/"),
    'gisc': rdflib.Namespace("http://gisc.ew.eea.europa.eu/rdf/"),
}

def res(packed_uri):
    ns_name, slug = packed_uri.split(':')
    return ns[ns_name][slug]

_exc = object() # marker object
def single_prop(graph, subject, predicate, default=_exc):
    value_list = list(graph.objects(subject, predicate))
    if len(value_list) == 0:
        if default is _exc:
            raise ValueError('Missing property %r for %r' %
                             (predicate, subject))
        else:
            return default
    elif len(value_list) > 1:
        raise ValueError('Expected single property %r for %r' %
                         (predicate, subject))
    else:
        return value_list[0]

class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Organization(Struct): pass
class Product(Struct): pass
class Resource(Struct): pass
class Property(Struct): pass

def map_organization(graph, org):
    name = single_prop(graph, org, res('foaf:name'))
    homepage = single_prop(graph, org, res('foaf:homepage'))
    return Organization(uri=unicode(org),
                        name=unicode(name),
                        homepage=unicode(homepage))

def extract_date(rdf_date):
    """
    extract a python ``datetime.date`` object from ``rdf_date``,
    assuming it's an ``xsd:date``.
    """
    year, month, day = map(int, str(rdf_date).split('-'))
    return datetime.date(year, month, day)

def map_product(graph, prod):
    title = single_prop(graph, prod, res('dcterms:title'))
    description = single_prop(graph, prod, res('dcterms:description'), None)
    homepage = single_prop(graph, prod, res('foaf:homepage'), None)
    organization = single_prop(graph, prod, res('dcterms:publisher'))
    modified = single_prop(graph, prod, res('dcterms:modified'), None)

    if description is not None:
        description = unicode(description)
    if homepage is not None:
        homepage = unicode(homepage)
    if modified is not None:
        modified = extract_date(modified)

    return Product(uri=unicode(prod),
                   title=unicode(title),
                   description=description,
                   homepage=homepage,
                   organization_uri=unicode(organization),
                   modified=modified)

class FilesystemDatasource(object):
    def __init__(self, data_path):
        self.data_path = data_path

    def _read_data(self):
        graph = Graph()
        for file_name in os.listdir(self.data_path):
            graph.parse(path.join(self.data_path, file_name), format="n3")
        return graph

    def list_organizations(self):
        graph = self._read_data()
        for org in graph.subjects(res('rdf:type'), res('foaf:Organization')):
            yield map_organization(graph, org)

    def get_organization(self, org_uri):
        graph = self._read_data()
        return map_organization(graph, rdflib.URIRef(org_uri))

    def list_products(self, organization=None):
        graph = self._read_data()

        filters = []
        if organization is not None:
            f = lambda product: product.organization_uri == organization
            filters.append(f)

        for prod in graph.subjects(res('rdf:type'), res('gisc:Product')):
            product = map_product(graph, prod)
            for f in filters:
                if not f(product):
                    break
            else:
                yield product
