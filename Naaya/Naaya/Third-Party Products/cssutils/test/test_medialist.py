__version__ = '0.51'

import unittest
import xml.dom

import cssutils.medialist


class MediaListTestCase(unittest.TestCase):

    def test_set(self):
        ml = cssutils.medialist.MediaList()

        self.assertEqual(0, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        ml.mediaText = u' print   , screen '        
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, screen', ml.mediaText)

        ml.mediaText = u' print , all  , screen '        
        self.assertEqual(1, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        self.assertRaises(xml.dom.SyntaxErr, ml._setMediaText, u'test')

    def test_append(self):
        ml = cssutils.medialist.MediaList()

        ml.appendMedium(u'print')
        self.assertEqual(1, ml.length)
        self.assertEqual(u'print', ml.mediaText)

        ml.appendMedium(u'screen')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, screen', ml.mediaText)

        # automatic del and append!        
        ml.appendMedium(u'print')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'screen, print', ml.mediaText)

    def test_appendAll(self):
        ml = cssutils.medialist.MediaList()
        ml.appendMedium(u'print')
        ml.appendMedium(u'tv')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, tv', ml.mediaText)

        ml.appendMedium(u'all')
        self.assertEqual(1, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        ml.appendMedium(u'print')
        self.assertEqual(1, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        self.assertRaises(xml.dom.InvalidCharacterErr, ml.appendMedium, u'test')

    def test_delete(self):
        ml = cssutils.medialist.MediaList()

        self.assertRaises(xml.dom.NotFoundErr, ml.deleteMedium, u'all')
        self.assertRaises(xml.dom.NotFoundErr, ml.deleteMedium, u'test')

        ml.appendMedium(u'print')
        ml.deleteMedium(u'print')
        self.assertEqual(0, ml.length)
        self.assertEqual(u'all', ml.mediaText)

    def test_item(self):
        ml = cssutils.medialist.MediaList()
        ml.appendMedium(u'print')
        ml.appendMedium(u'screen')

        self.assertEqual(u'print', ml.item(0))
        self.assertEqual(u'screen', ml.item(1))
        self.assertEqual(None, ml.item(2))
    
        
if __name__ == '__main__':
    unittest.main() 