import sys
import os
import tempfile
from contextlib import contextmanager
import json
import optparse

from javadb import java_vm, db_connection
from geonetwork_schema import list_settings, list_metadata
from repoze.configuration import execute as execute_config

def config_directive(declaration):
    declaration.expect(dict, names=['output_file'])
    output_file = declaration.string('output_file', None)
    def callback():
        declaration.registry['output_file'] = output_file
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

@contextmanager
def output_file(context):
    output_path = context.registry['output_file']
    if output_path is not None:
        f = tempfile.NamedTemporaryFile(delete=False)
        yield f
        f.close()
        os.rename(f.name, output_path)
    else:
        yield sys.stdout
        sys.stdout.write('\n')

def dump_harvesting_data(context, db_statement):
    output = {
        'documents': list(list_metadata(db_statement)),
        'sources': list(list_sources(db_statement)),
    }
    with output_file(context) as f:
        f.write(json.dumps(output))

def main():
    usage = "usage: %prog path/to/config.yaml <print_settings|dump_harvesting>"
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
            else:
                option_parser.error("Unknown command %r" % args[1])

if __name__ == '__main__':
    main()
