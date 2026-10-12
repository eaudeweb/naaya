"""Convert a Python 2 Data.fs to Python 3 with zodbupdate, decoding py2 str as UTF-8.

Usage: parts/<instance>/bin/interpreter py3migration/convert_py3.py Data.fs analysis.json
"""
import json
import logging
import sys
import time

import ZODB.FileStorage
import ZODB.serialize
import zodbupdate.convert
import zodbupdate.main
from importlib.metadata import entry_points

# Non-UTF-8 text in attributes found by analyze_py2.py is decoded with these.
FALLBACKS = ['cp1252', 'latin-1']

# Binary attributes that may hold bytes which happen to be valid UTF-8.
BINARY = [
    'naaya.content.news.news_item NyNews smallpicture',
    'naaya.content.news.news_item NyNews bigpicture',
    'naaya.content.story.story_item NyStory frontpicture',
    'Products.NaayaCore.SyndicationTool.ScriptChannel ScriptChannel Python_magic',
    'Products.NaayaCore.SyndicationTool.ScriptChannel ScriptChannel _code',
] + ['naaya.content.hexfolder.hexfolder_item NyHexfolder picture_%d' % i
     for i in range(20)]

# Missing 5.0's Missing._Missing shim is broken (deferredimport reads "Missing.V" as a module).
RENAMES = {('Missing._Missing', name): ('Missing', name)
           for name in ('V', 'Value', 'MV', 'Missing', 'notMissing')}
# Zope 2.13 local site managers; zope.site has the same classes.
RENAMES.update({('zope.app.component.site', name): ('zope.site.site', name)
                for name in ('LocalSiteManager', 'SiteManagementFolder',
                             '_LocalAdapterRegistry')})


def declared_attributes():
    """Attributes that installed packages already declare zodbupdate rules for."""
    declared = set()
    for entry_point in entry_points().select(group='zodbupdate.decode'):
        declared.update(entry_point.load())
    return declared


def rules_from_analysis(path):
    """Binary rule where any value is binary, decode rule where any is non-UTF-8 text."""
    binary, text = set(BINARY), set()
    with open(path) as f:
        attributes = json.load(f)['attributes']
    for key, kinds in attributes.items():
        module, cls, attr = key.split(' ', 2)
        if not attr.isidentifier():
            continue  # nested values; reported again by scan_py3.py
        if kinds.get('binary'):
            binary.add(key)
        elif kinds.get('text8'):
            text.add(key)
    declared = declared_attributes()
    return binary - declared, text - binary - declared


def build_decoders(analysis_path):
    decoders = zodbupdate.convert.load_decoders(encoding_fallbacks=FALLBACKS)
    binary, text = rules_from_analysis(analysis_path)
    for key in binary:
        module, cls, attr = key.split(' ')
        decoders.setdefault((module, cls), []).append(
            zodbupdate.convert.encode_binary(attr))
    for key in text:
        module, cls, attr = key.split(' ')
        decoders.setdefault((module, cls), []).append(
            zodbupdate.convert.decode_attribute(attr, 'utf-8', FALLBACKS))
    print('binary rules: %d, text fallback rules: %d' % (len(binary), len(text)))
    for key in sorted(binary):
        print('  binary', key)
    for key in sorted(text):
        print('  text  ', key)
    return decoders


def main(datafs, analysis_path):
    logging.basicConfig(level=logging.WARNING, format='%(message)s')
    decoders = build_decoders(analysis_path)
    # create_updater replaces per-class decoder lists with load_decoders()
    zodbupdate.convert.load_decoders = lambda **kw: decoders
    zodbupdate.convert.update_magic_data_fs(datafs)
    storage = ZODB.FileStorage.FileStorage(datafs)
    updater = zodbupdate.main.create_updater(
        storage,
        default_renames=RENAMES,
        convert_py3=True,
        encoding='utf-8',
        encoding_fallbacks=FALLBACKS,
    )
    updater()
    print('Packing ...')
    storage.pack(time.time(), ZODB.serialize.referencesf)
    storage.close()
    print('Done.')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
