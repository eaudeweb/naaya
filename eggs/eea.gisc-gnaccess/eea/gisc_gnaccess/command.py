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
    declaration.expect(dict, names=['report_points_of_contact', 'report_distribution_info',
                                     'organisation_icon', 'document_icon', 'role_icon', 'email_icon', 'url_icon'])
    report_points_of_contact = declaration.string('report_points_of_contact', None)
    report_distribution_info = declaration.string('report_distribution_info', None)
    organisation_icon = declaration.string('organisation_icon', None)
    document_icon = declaration.string('document_icon', None)
    role_icon = declaration.string('role_icon', None)
    email_icon = declaration.string('email_icon', None)
    url_icon = declaration.string('url_icon', None)
    def callback():
        declaration.registry['report_points_of_contact'] = report_points_of_contact
        declaration.registry['report_distribution_info'] = report_distribution_info
        declaration.registry['organisation_icon'] = organisation_icon
        declaration.registry['document_icon'] = document_icon
        declaration.registry['role_icon'] = role_icon
        declaration.registry['email_icon'] = email_icon
        declaration.registry['url_icon'] = url_icon
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
    organisations2 = {}
    for m in metadatas:
        id = str(m['id'])
        data = m['data'].encode('utf-8')
        title = get_title(data)
        contacts = get_points_of_contact(data)
        for c in contacts:
            org_name = c.get('organisation', '')
            if type(c.get('email', [])) == type([]):
                emails = c.get('email', [])
            else:
                emails = [c.get('email', '')]
            role = c.get('role', '')
            
            if org_name not in organisations:
                organisations[org_name] = {}
            if title not in organisations[org_name]:
                organisations[org_name][title] = {}
            if role not in organisations[org_name][title]:
                organisations[org_name][title][role] = []
            organisations[org_name][title][role].extend(emails)
    
    organisation_icon = context.registry['organisation_icon'] 
    document_icon = context.registry['document_icon']
    role_icon = context.registry['role_icon']
    email_icon = context.registry['email_icon']
    jstree = []
    for org, v in organisations.iteritems():
        doc_tree = []
        for title, v2 in v.iteritems():
            role_tree = []
            for role, emails in v2.iteritems():
                email_tree = []
                for email in emails:
                    email_tree.append({'data': {'title': email, 'icon': email_icon, 'attributes': {'href': 'mailto:'+email}}})
                role_tree.append({'data': {'title': role, 'icon': role_icon}, 'children': email_tree})
            if len(role_tree) == 1 and role_tree[0]['data']['title'] == '':
                email_tree = role_tree[0]['children']
                doc_tree.append({'data': {'title': title, 'icon': document_icon}, 'children': email_tree})
            else:
                doc_tree.append({'data': {'title': title, 'icon': document_icon}, 'children': role_tree})
        jstree.append({'data': {'title': org, 'icon': organisation_icon}, 'state': 'open', 'children': doc_tree})

    with output_file(context, 'report_points_of_contact') as f:
        f.write(json.dumps(jstree))

def dump_distribution_info_report(context, db_statement):
    gen = gen_metadata(db_statement)
    metadatas = [m for m in gen if m['isTemplate'] == 'n']

    document_icon = context.registry['document_icon']
    url_icon = context.registry['url_icon']   
    jstree = []
    for m in metadatas:
        data = m['data'].encode('utf-8')
        title = get_title(data)
        url_list = get_distribution_info(data)
        url_tree = []
        for url in url_list:
            url_tree.append({'data': {'title': url, 'icon': url_icon, 'attributes': {'href': url}}})
        jstree.append({'data': {'title': title, 'icon': document_icon}, 'children': url_tree})

    with output_file(context, 'report_distribution_info') as f:
        f.write(json.dumps(jstree))

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
