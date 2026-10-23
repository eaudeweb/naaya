"""Every pluggable content type must load again from the storage after a commit."""
from unittest import mock

import transaction
from persistent import Persistent

from naaya.content.base.discover import get_pluggable_content
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

TITLE = 'Bruxelles – \xe9\xe8\xe0 ă \xee ș ț'
GEO = {'geo_location.lat': '50.85', 'geo_location.lon': '4.35',
       'geo_location.address': TITLE}
# Data the add functions validate, per meta type
EXTRA = {
    'Naaya Event': {'start_date': '10/10/2026', 'end_date': '11/10/2026'},
    'Naaya GeoPoint': GEO,
    'Naaya Media File': {'_skip_videofile_check': True},
    'Naaya Meeting': dict(GEO, **{'interval.start_date': '20/06/2026',
                                  'interval.end_date': '25/06/2026',
                                  'interval.all_day': True,
                                  'contact_person': TITLE,
                                  'contact_email': 'a@example.com'}),
    'Naaya Youtube': {'youtube_id': 'dQw4w9WgXcQ', 'iframe_width': '640',
                      'iframe_height': '360'},
    'Naaya Best Practice': dict(GEO, coverage=TITLE, description=TITLE,
                                gstc_criteria=['x'], landscape_type=['x'],
                                topics=['x'], category='x'),
    'Naaya Certificate': {'coverage': TITLE, 'category': 'x',
                          'administrative_level': 'x', 'sustainability': 'x',
                          'credibility': 'x', 'certificate_services': ['x']},
    'Naaya Good Practice Business': dict(GEO, coverage=TITLE, description=TITLE,
                                         gstc_industry=['x'], landscape_type=['x'],
                                         topics=['x'], category='x'),
}
# Added only through a request with uploaded pictures
SKIP = {'Naaya Hex Folder'}


def load_tree(ob, seen):
    """Unpickle ob and every persistent object it references."""
    if id(ob) in seen:
        return
    seen.add(id(ob))
    if isinstance(ob, Persistent):
        ob._p_activate()
        if hasattr(ob, '__dict__'):
            values = list(ob.__dict__.values())
        else:
            # BTrees keep their data outside __dict__
            values = [v for item in ob.items() for v in item]
    elif isinstance(ob, (list, tuple, set, frozenset)):
        values = list(ob)
    elif isinstance(ob, dict):
        values = list(ob.keys()) + list(ob.values())
    else:
        return
    for value in values:
        load_tree(value, seen)


class PersistenceTest(NaayaTestCase):

    # the Youtube add function checks the video id on youtube.com
    @mock.patch('urllib.request.urlopen')
    def test_content_types_reload(self, urlopen):
        folder = self.portal.info
        added = {}
        not_added = []
        for meta_type, config in sorted(get_pluggable_content().items()):
            constructors = config.get('constructors')
            if not constructors or meta_type in SKIP:
                continue
            ob_id = 'persist%d' % len(added)
            savepoint = transaction.savepoint()
            try:
                constructors[-1](folder, id=ob_id, title=TITLE, contributor='admin',
                                 submitted=1, **EXTRA.get(meta_type, {}))
            except Exception as e:
                savepoint.rollback()
                not_added.append('%s: %s: %s' % (meta_type, type(e).__name__, e))
                continue
            added[meta_type] = ob_id
        self.assertEqual(not_added, [])
        transaction.commit()

        conn = self.app._p_jar.db().open()
        try:
            fresh = conn.root()['Application'][self.portal.getId()].info
            for meta_type, ob_id in added.items():
                with self.subTest(meta_type=meta_type):
                    ob = fresh._getOb(ob_id)
                    load_tree(ob, set())
                    self.assertEqual(ob.meta_type, meta_type)
                    self.assertEqual(ob.title, TITLE)
        finally:
            conn.close()
