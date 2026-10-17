""" Watermark applied to photos """
import unittest
from io import BytesIO
from types import SimpleNamespace

from PIL import Image

from Products.NaayaPhotoArchive.NyPhoto import NyPhoto


class FakePhoto(object):
    _apply_watermark = NyPhoto._apply_watermark
    _photo_quality = NyPhoto._photo_quality

    def __init__(self, text):
        self.aq_parent = SimpleNamespace(watermark_text=text)


class WatermarkTest(unittest.TestCase):

    def test_apply_watermark(self):
        original = BytesIO()
        Image.new('RGB', (200, 120), 'black').save(original, 'JPEG')
        original.seek(0)
        result = FakePhoto('Naaya')._apply_watermark(original)
        img = Image.open(result)
        self.assertEqual(img.format, 'JPEG')
        self.assertEqual(img.size, (200, 120))
        self.assertNotEqual(img.getextrema(), ((0, 0),) * 3)

    def test_image_smaller_than_text(self):
        original = BytesIO()
        Image.new('RGB', (1, 1), 'black').save(original, 'PNG')
        original.seek(0)
        result = FakePhoto('Naaya')._apply_watermark(original)
        self.assertEqual(Image.open(result).size, (1, 1))
