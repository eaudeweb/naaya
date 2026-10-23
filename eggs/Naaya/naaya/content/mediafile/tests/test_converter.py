import os
import shutil
import tempfile
import unittest
from unittest import mock

from naaya.content.mediafile.converters import MediaConverter
from naaya.content.mediafile.mediafile_item import addNyMediaFile
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase


class Media2Mp4Test(unittest.TestCase):

    def convert(self, resolution):
        tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tempdir)
        mediafile = mock.Mock()
        mediafile.get_filename.return_value = os.path.join(tempdir, 'in.avi')
        process = mock.Mock()
        process.wait.return_value = 0
        with mock.patch.object(MediaConverter, 'can_convert',
                               return_value=True), \
                mock.patch.object(MediaConverter, 'CONVERSION_TOOL', 'ffmpeg'), \
                mock.patch.object(MediaConverter, 'get_resolution',
                                  return_value=resolution), \
                mock.patch.object(MediaConverter.tempfile, 'mkdtemp',
                                  return_value=tempdir), \
                mock.patch.object(MediaConverter.subprocess, 'Popen',
                                  return_value=process) as popen, \
                mock.patch.object(MediaConverter, '_finish') as finish:
            MediaConverter.media2mp4(mediafile)
        finish.assert_called_once()
        cmd = popen.call_args[0][0]
        return cmd[cmd.index('-s') + 1]

    def test_scale_down_to_720p(self):
        self.assertEqual(self.convert((1000, 750)), '960x720')

    def test_round_to_multiple_of_16(self):
        self.assertEqual(self.convert((650, 370)), '640x368')


class IsAudioTest(NaayaTestCase):

    def test_no_media(self):
        self.portal.manage_install_pluggableitem('Naaya Media File')
        ob_id = addNyMediaFile(self.portal.info, title='No media',
                               _skip_videofile_check=True)
        self.assertFalse(self.portal.info[ob_id].is_audio())
