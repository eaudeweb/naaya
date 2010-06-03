import sys
import os
import tempfile
from contextlib import contextmanager
import json
import optparse

from javadb import java_vm, db_connection
from geonetwork_schema import list_settings, list_metadata
from repoze.configuration import execute as execute_config

from geonetwork_schema import gen_metadata
from xml_parser import get_title, get_points_of_contact, get_distribution_info
from unicode_csv import UnicodeWriter

def config_directive(declaration):
    declaration.expect(dict, names=['report_points_of_contact', 'report_distribution_info'])
    report_points_of_contact = declaration.string('report_points_of_contact', None)
    report_distribution_info = declaration.string('report_distribution_info', None)
    def callback():
        declaration.registry['report_points_of_contact'] = report_points_of_contact
        declaration.registry['report_distribution_info'] = report_distribution_info
    declaration.action(callback)

def print_settings(settings, level=0):
    print '    '*level + repr(settings)
    for s in settings.values():
        print_settings(s, level+1)

def parse_source_info(node):
    method_name = node.value
    for site_entry in node.children_with_name('site'):
        yield {
            'name': site_entry.child_value('name'),
            'uuid': site_entry.child_value('uuid'),
            'url': "http://%s:%s/%s" % (site_entry.child_value('host'),
                                        site_entry.child_value('port'),
                                        site_entry.child_value('servlet')),
            'method': 'geonetwork',
        }

def list_sources(db_statement):
    settings = list_settings(db_statement)
    harvesting_entry = list(settings.children_with_name('harvesting'))[0]
    for node in harvesting_entry.children_with_name('node'):
        for source_info in parse_source_info(node):
            yield source_info

def dump_harvesting_data(context, db_statement):
    output = {
        'documents': list(list_metadata(db_statement)),
        'sources': list(list_sources(db_statement)),
    }
    print json.dumps(output, sort_keys=True, indent=4)

@contextmanager
def output_file(context, registry_name):
    output_path = context.registry[registry_name]
    if output_path is not None:
        f = tempfile.NamedTemporaryFile(delete=False)
        yield f
        f.close()
        os.rename(f.name, output_path)
    else:
        yield sys.stdout
        sys.stdout.write('\n')

def dump_points_of_contact_report(context, db_statement):
    gen = gen_metadata(db_statement)
    metadatas = [m for m in gen if m['isTemplate'] == 'n']
    organisations = {}
    for m in metadatas:
        id = str(m['id'])
        title = get_title(m['data'])
        contacts = get_points_of_contact(m['data'])
        for c in contacts:
            if c['organisation'] not in organisations:
                organisations[c['organisation']] = []
            organisations[c['organisation']].append({
                'id': id,
                'title': title,
                'email': c['email'],
            })
    with output_file(context, 'report_points_of_contact') as f:
        writer = UnicodeWriter(f)
        writer.writerow(['Organisation', 'Id', 'Title', 'Email'])
        for k, v in organisations.iteritems():
            o = v[0]
            id, title, email = o['id'], o['title'], o['email']
            writer.writerow([k, id, title, email])
            for o in v[1:]:
                id, title, email = o['id'], o['title'], o['email']
                writer.writerow(['', id, title, email])

def dump_distribution_info_report(context, db_statement):
    gen = gen_metadata(db_statement)
    metadatas = [m for m in gen if m['isTemplate'] == 'n']
    with output_file(context, 'report_distribution_info') as f:
        writer = UnicodeWriter(f)
        writer.writerow(['Id', 'Title', 'Distibution url'])
        for m in metadatas:
            id = str(m['id'])
            title = get_title(m['data'])
            url = get_distribution_info(m['data'])
            writer.writerow([id, title, url])

def main():
    usage = "usage: %prog path/to/config.yaml <print_settings|dump_harvesting|report_points_of_contact|report_distribution_info>"
    option_parser = optparse.OptionParser(usage=usage)
    (options, args) = option_parser.parse_args()

    if len(args) != 2:
        option_parser.error("incorrect number of arguments")

    context = execute_config(args[0])
    with java_vm(context):
        with db_connection(context) as db_statement:
            if args[1] == 'print_settings':
                print_settings(list_settings(db_statement))
            elif args[1] == 'dump_harvesting':
                dump_harvesting_data(context, db_statement)
            elif args[1] == 'report_points_of_contact':
                dump_points_of_contact_report(context, db_statement)
            elif args[1] == 'report_distribution_info':
                dump_distribution_info_report(context, db_statement)
            else:
                option_parser.error("Unknown command %r" % args[1])

if __name__ == '__main__':
    main()
