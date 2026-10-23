import logging
import unittest
from unittest.mock import Mock, patch

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.naayaUpdater import utils
from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.updates.update_map_engines import UpdateMapEngines


class MarkerUpdate(UpdateScript):
    """ Sets a marker on the portal, or fails after setting it """
    fail = False

    def _update(self, portal):
        portal.updater_marker = 'changed'
        self.log.info('marker set')
        if self.fail:
            raise ValueError('update failed')
        return True


class UpdateScriptTest(NaayaTestCase):

    def afterSetUp(self):
        self.portal.updater_marker = 'original'
        transaction.commit()

    def beforeTearDown(self):
        self.portal.updater_marker = 'original'
        transaction.commit()

    def script(self, **kw):
        script = MarkerUpdate(**kw)
        script.id = 'marker_update'
        return script.__of__(self.portal)

    def test_dry_run_aborts(self):
        success, log_data = self.script().update(self.portal, True)
        self.assertTrue(success)
        self.assertIn('marker set', log_data)
        self.assertEqual(self.portal.updater_marker, 'original')

    def test_run_commits(self):
        success, log_data = self.script().update(self.portal, False)
        self.assertTrue(success)
        transaction.abort()
        self.assertEqual(self.portal.updater_marker, 'changed')

    def test_failure_aborts(self):
        script = self.script()
        script.fail = True
        success, log_data = script.update(self.portal, False)
        self.assertFalse(success)
        self.assertIn('Update script failed - "update failed"', log_data)
        self.assertIn('Traceback', log_data)
        self.assertEqual(self.portal.updater_marker, 'original')

    def test_one_log_handler(self):
        script = self.script()
        script.update(self.portal, True)
        success, log_data = script.update(self.portal, True)
        self.assertEqual(
            len(logging.getLogger('naayaUpdater.marker_update').handlers), 1)
        self.assertEqual(log_data.count('marker set'), 1)

    def test_manage_update_dry_run(self):
        script = self.script()
        request = Mock(REQUEST_METHOD='POST')
        request.form = {'action': 'Dry run',
                        'portal_paths': ['/'.join(
                            self.portal.getPhysicalPath())]}
        with patch.object(MarkerUpdate, 'update_template') as template, \
                patch.object(MarkerUpdate, 'add_log', create=True) as add_log:
            script.manage_update(request)
        report = template.call_args.kwargs['report']
        self.assertIn('<h4>SUCCESS</h4>', report)
        self.assertIn('marker set', report)
        add_log.assert_not_called()
        self.assertEqual(self.portal.updater_marker, 'original')


class UpdateMapEnginesTest(NaayaTestCase):

    def portal_map(self):
        portal_map = self.portal.getGeoMapTool()
        # load the state, or __dict__ changes are lost when it is loaded
        portal_map._p_activate()
        return portal_map

    def run_update(self):
        script = UpdateMapEngines()
        script.id = 'update_map_engines'
        script = script.__of__(self.portal)
        script._setup_logger()
        self.assertTrue(script._update(self.portal))
        return self.portal.getGeoMapTool()

    def test_yahoo_engine_replaced(self):
        portal_map = self.portal_map()
        portal_map.__dict__.update({'map_engine': 'yahoo',
                                    'mapsapikey': ['yahoo-key'],
                                    'default_type': 'YAHOO_MAP_SAT'})
        portal_map = self.run_update()
        self.assertEqual(portal_map.current_engine, 'openlayers')
        self.assertIn('engine_openlayers', portal_map.objectIds())
        self.assertNotIn('mapsapikey', portal_map.__dict__)
        self.assertNotIn('map_engine', portal_map.__dict__)

    def test_google_keys(self):
        portal_map = self.portal_map()
        if 'engine_google' in portal_map.objectIds():
            portal_map.manage_delObjects(['engine_google'])
        portal_map.__dict__.update({'googleApiKey': ['k1', 'k2'],
                                    'default_type': 'YAHOO_MAP_HYB',
                                    'enableKeyControls': False})
        portal_map = self.run_update()
        engine = portal_map.get_map_engine('google')
        self.assertEqual(engine.api_keys, 'k1\nk2')
        self.assertEqual(engine.base_layer, 'hybrid')
        self.assertFalse(engine.allow_mouse_scroll)

    def test_renamed_properties(self):
        portal_map = self.portal_map()
        portal_map.__dict__.update({'center_locality': 'Romania',
                                    'map_height': 600,
                                    'detailed_map_height': 300,
                                    'detailed_map_width': 200})
        portal_map = self.run_update()
        self.assertEqual((portal_map.initial_address, portal_map.map_height_px,
                          portal_map.objmap_height_px,
                          portal_map.objmap_width_px),
                         ('Romania', 600, 300, 200))
        for name in ('center_locality', 'map_height', 'detailed_map_height',
                     'detailed_map_width'):
            self.assertNotIn(name, portal_map.__dict__)


class UtilsTest(unittest.TestCase):

    def test_get_template_content(self):
        self.assertEqual(utils.get_template_content(Mock(_text='<p/>')),
                         '<p/>')
        form = Mock(spec=['data'], data='café'.encode('utf-8'))
        self.assertEqual(utils.get_template_content(form), 'café')
        self.assertEqual(utils.get_template_content(
            Mock(spec=['data'], data='text')), 'text')

    def test_read_file(self):
        import os
        import tempfile
        with tempfile.NamedTemporaryFile('wb', suffix='.txt',
                                         delete=False) as f:
            f.write('café'.encode('utf-8'))
        self.addCleanup(os.remove, f.name)
        self.assertEqual(utils.readFile(f.name), 'café')
        self.assertEqual(utils.readFile(f.name, 'rb'),
                         'café'.encode('utf-8'))

    def test_html_decode(self):
        self.assertEqual(utils.html_decode('&lt;a href=&quot;x&quot;&gt;'
                                           ' &amp; &apos;'),
                         '<a href="x"> & \'')

    def test_convert_lines_to_list(self):
        self.assertEqual(utils.convertLinesToList('a\r\n\r\nb'), ['a', 'b'])
        self.assertEqual(utils.convertLinesToList(''), [])
        self.assertEqual(utils.convertLinesToList(['x']), ['x'])
