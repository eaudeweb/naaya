import urllib
from os import path

import jinja2
import rdflib
from webob import Response
from webob.dec import wsgify
from webob.exc import HTTPNotFound

from fsdata import res
from fsdata import single_prop
from fsdata import extract_date
from fsdata import FilesystemDatasource

def setup_jinja():
    loader = jinja2.PackageLoader('edw.gisc_catalogue')
    jinja_env = jinja2.Environment(loader=loader)
    jinja_env.filters['urlencode'] = lambda s: urllib.quote(s, '')
    return jinja_env

jinja_env = setup_jinja()

def template(tmpl_name, **kwargs):
    return jinja_env.get_template(tmpl_name).render(**kwargs)

def read_media_file(name):
    f = open(path.join(path.dirname(__file__), 'www', name), 'rb')
    data = f.read()
    f.close()
    return data

def describe_resource_frag(resource, request):
    graph = request.environ['gisc.graph']

    data_by_predicate = {}
    for subj, pred, obj in graph.triples((resource, None, None)):
        data_by_predicate.setdefault(pred, []).append(obj)

    props = []
    for prop_uri, values in data_by_predicate.iteritems():
        try:
            prop_label, converter = property_value_map[prop_uri]
        except KeyError:
            prop_label = unicode(prop_uri)
            converter = convert_unicode

        if prop_label is None:
            continue # skip this property

        html_values = [converter(value, request) for value in values]
        props.append( (prop_label, html_values) )

    return template('describe_resource_frag.html', props=props)

def resource_links_frag(resource, request):
    graph = request.environ['gisc.graph']

    data_by_predicate = {}
    for subj, pred, obj in graph.triples((None, None, resource)):
        data_by_predicate.setdefault(pred, []).append(subj)

    links_map = []
    for pred, subj_list in data_by_predicate.iteritems():
        rel_label = get_reverse_relation_label(obj, pred, request)
        links_list = [convert_resource_link(res, request) for res in subj_list]
        links_map.append((rel_label, links_list))

    return template('resource_links_frag.html', links_map=links_map)

@wsgify
def describe_resource_app(request):
    resource = rdflib.URIRef(request.GET['uri'])
    kwargs = {
        'label': get_resource_label(resource, request),
        'resource_frag': describe_resource_frag(resource, request),
        'links_frag': resource_links_frag(resource, request),
        'css_data': read_media_file('describe_resource.css'),
    }
    return Response(template('describe_resource.html', **kwargs))

@wsgify
def list_organizations_app(request):
    graph = request.environ['gisc.graph']
    orgs = list(graph.subjects(res('rdf:type'), res('foaf:Organization')))
    print orgs
    kwargs = {
        'links_list': [convert_resource_link(org, request) for org in orgs],
        'css_data': read_media_file('describe_resource.css'),
    }
    return Response(template('index.html', **kwargs))

def href_describe_resource(res, request):
    return "%s?uri=%s" % (request.environ['gisc.res_app_url'],
                          urllib.quote(unicode(res), ''))

def get_reverse_relation_label(obj, pred, request):
    graph = request.environ['gisc.graph']
    subject_type = single_prop(graph, obj, res('rdf:type'))
    return reverse_relation_label.get((subject_type, pred), unicode(pred))

def get_resource_label(resource, request):
    graph = request.environ['gisc.graph']
    for predicate in (res('dcterms:title'), res('foaf:name')):
        label = single_prop(graph, resource, predicate, None)
        if label is not None:
            break
    else:
        label = resource

    return unicode(label)

def convert_unicode(value, request):
    return unicode(value)

def convert_href(value, request):
    return jinja2.utils.urlize(value)

def convert_available_from(value, request):
    graph = request.environ['gisc.graph']
    assert (res('gisc:DownloadLink') in
            graph.objects(value, res('rdf:type')))
    mime_type = single_prop(graph, value, res('dcterms:format'))
    download_url = single_prop(graph, value, res('gisc:url'))
    return jinja2.utils.urlize(download_url, 40) + ' (%s)' % mime_type

def convert_file_size(value, request):
    return jinja2.filters.do_filesizeformat(int(value))

def convert_temporal(value, request):
    graph = request.environ['gisc.graph']
    assert (res('dcterms:PeriodOfTime') in
            graph.objects(value, res('rdf:type')))
    start_date = single_prop(graph, value, res('gisc:startDate'))
    end_date = single_prop(graph, value, res('gisc:endDate'))
    return u"From %s to %s" % (extract_date(start_date),
                               extract_date(end_date))

def convert_spatial(value, request):
    graph = request.environ['gisc.graph']
    assert (res('dcterms:Jurisdiction') in
            graph.objects(value, res('rdf:type')))
    country_code = single_prop(graph, value, res('gisc:countryCode'))
    return u"Country: %s" % country_code

def convert_resource_link(value, request):
    label = get_resource_label(value, request)
    escaped_href = jinja2.utils.escape(href_describe_resource(value, request))
    return u'<a href="%s">%s</a>' % (escaped_href, label)

property_value_map = {
    res('rdf:type'): (None, None),
    res('foaf:name'): ('Name', convert_unicode),
    res('foaf:homepage'): ('Homepage', convert_href),
    res('gisc:availableFrom'): ('Download', convert_available_from),
    res('gisc:fileSize'): ('File size', convert_file_size),
    res('gisc:indicator'): ('Indicators', convert_unicode),
    res('dcterms:title'): ('Title', convert_unicode),
    res('dcterms:publisher'): ('Organization', convert_resource_link),
    res('dcterms:temporal'): ('Temporal extent', convert_temporal),
    res('dcterms:spatial'): ('Spatial extent', convert_spatial),
    res('dcterms:modified'): ('Last modified', convert_unicode),
    res('dcmi:isPartOf'): ('Part of product', convert_resource_link),
    res('dcterms:description'): ('Description', convert_unicode),
}

reverse_relation_label = {
    (res('gisc:Product'), res('dcmi:isPartOf')): "Datasets",
    (res('foaf:Organization'), res('dcterms:publisher')): "Products",
}

def factory(global_conf, data_path):
    data_path = path.join(global_conf['here'], data_path)
    data_source = FilesystemDatasource(data_path)
    return CatalogueApp(data_source)

class CatalogueApp(object):
    def __init__(self, data_source):
        self.data_source = data_source

    @wsgify
    def __call__(self, request):
        request.environ.update({
            'gisc.graph': self.data_source._read_data(),
            'gisc.res_app_url': request.application_url + '/res',
        })

        if request.path == '/':
            return request.get_response(list_organizations_app)

        elif request.path == '/res':
            return request.get_response(describe_resource_app)

        else:
            return HTTPNotFound()
