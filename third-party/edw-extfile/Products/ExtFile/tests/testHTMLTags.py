#
# Test HTML quoting of link and tag methods
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ExtFile')

from Products.ExtFile.testing import ExtFileTestCase
from Products.ExtFile.testing import gifImage
from Products.ExtFile.testing import notImage


class TestExtFileLink(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder_url = self.folder.absolute_url()
        self.addExtFile(id='file', file=notImage)

    def testDefaultText(self):
        self.assertEqual(self.file.link(),
            '<a href="%s/file" title="">file</a>' % self.folder_url)

    def testDefaultTitle(self):
        self.file.title = 'The File'
        self.assertEqual(self.file.link(),
            '<a href="%s/file" title="The File">The File</a>' % self.folder_url)

    def testText(self):
        self.assertEqual(self.file.link(text='The File'),
            '<a href="%s/file" title="">The File</a>' % self.folder_url)

    def testTextQuoting(self):
        self.assertEqual(self.file.link(text='<The File>'),
            '<a href="%s/file" title="">&lt;The File&gt;</a>' % self.folder_url)

    def testStructure(self):
        self.assertEqual(self.file.link(text='<img src="" />', structure=True),
            '<a href="%s/file" title=""><img src="" /></a>' % self.folder_url)

    def testTitle(self):
        self.assertEqual(self.file.link(title='The File'),
            '<a href="%s/file" title="The File">file</a>' % self.folder_url)

    def testTitleQuoting(self):
        self.assertEqual(self.file.link(title='The "File"'),
            '<a href="%s/file" title="The &quot;File&quot;">file</a>' % self.folder_url)

    def testCssClass(self):
        self.assertEqual(self.file.link(css_class='file-download'),
            '<a href="%s/file" title="" class="file-download">file</a>' % self.folder_url)

    def testCustom(self):
        self.assertEqual(self.file.link(foobar='baz'),
            '<a href="%s/file" title="" foobar="baz">file</a>' % self.folder_url)

    def testIcon(self):
        self.assertEqual(self.file.link(icon=1),
            '<a href="%s/file?icon=1" title="">file</a>' % self.folder_url)

    def testPreview(self):
        # Nonsense, but works ;-)
        self.assertEqual(self.file.link(preview=1),
            '<a href="%s/file?preview=1" title="">file</a>' % self.folder_url)


class TestPreviewLink(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder_url = self.folder.absolute_url()
        self.addExtImage(id='image', file=gifImage)

    def testDefaultText(self):
        self.assertEqual(self.image.preview_link(),
            '<a href="%s/image?preview=1" title="">image</a>' % self.folder_url)

    def testDefaultTitle(self):
        self.image.title = 'The Preview'
        self.assertEqual(self.image.preview_link(),
            '<a href="%s/image?preview=1" title="The Preview">The Preview</a>' % self.folder_url)

    def testText(self):
        self.assertEqual(self.image.preview_link(text='The Preview'),
            '<a href="%s/image?preview=1" title="">The Preview</a>' % self.folder_url)

    def testTextQuoting(self):
        self.assertEqual(self.image.preview_link(text='<The Preview>'),
            '<a href="%s/image?preview=1" title="">&lt;The Preview&gt;</a>' % self.folder_url)

    def testStructure(self):
        self.assertEqual(self.image.preview_link(text='<img src="" />', structure=True),
            '<a href="%s/image?preview=1" title=""><img src="" /></a>' % self.folder_url)

    def testTitle(self):
        self.assertEqual(self.image.preview_link(title='The Preview'),
            '<a href="%s/image?preview=1" title="The Preview">image</a>' % self.folder_url)

    def testTitleQuoting(self):
        self.assertEqual(self.image.preview_link(title='The "Preview"'),
            '<a href="%s/image?preview=1" title="The &quot;Preview&quot;">image</a>' % self.folder_url)

    def testCssClass(self):
        self.assertEqual(self.image.preview_link(css_class='image-download'),
            '<a href="%s/image?preview=1" title="" class="image-download">image</a>' % self.folder_url)

    def testCustom(self):
        self.assertEqual(self.image.preview_link(foobar='baz'),
            '<a href="%s/image?preview=1" title="" foobar="baz">image</a>' % self.folder_url)


class TestExtImageTag(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder_url = self.folder.absolute_url()
        self.addExtImage(id='image', file=gifImage)

    def testDefault(self):
        self.assertEqual(self.image.tag(),
            '<img src="%s/image" alt="" title="" height="16" width="16" />' % self.folder_url)

    def testDefaultAlt(self):
        self.image.alt = 'The Image'
        self.assertEqual(self.image.tag(),
            '<img src="%s/image" alt="The Image" title="" height="16" width="16" />' % self.folder_url)

    def testDefaultTitle(self):
        self.image.title = 'The Image'
        self.assertEqual(self.image.tag(),
            '<img src="%s/image" alt="" title="The Image" height="16" width="16" />' % self.folder_url)

    def testAlt(self):
        self.assertEqual(self.image.tag(alt='The Image'),
            '<img src="%s/image" alt="The Image" title="" height="16" width="16" />' % self.folder_url)

    def testAltQuoting(self):
        self.assertEqual(self.image.tag(alt='<The Image>'),
            '<img src="%s/image" alt="&lt;The Image&gt;" title="" height="16" width="16" />' % self.folder_url)

    def testTitle(self):
        self.assertEqual(self.image.tag(title='The Image'),
            '<img src="%s/image" alt="" title="The Image" height="16" width="16" />' % self.folder_url)

    def testTitleQuoting(self):
        self.assertEqual(self.image.tag(title='The "Image"'),
            '<img src="%s/image" alt="" title="The &quot;Image&quot;" height="16" width="16" />' % self.folder_url)

    def testWidthHeight(self):
        self.assertEqual(self.image.tag(width=32, height=32),
            '<img src="%s/image" alt="" title="" height="32" width="32" />' % self.folder_url)

    def testScale(self):
        self.assertEqual(self.image.tag(scale=0.5),
            '<img src="%s/image" alt="" title="" height="8" width="8" />' % self.folder_url)

    def testCssClass(self):
        self.assertEqual(self.image.tag(css_class="image-fullsize"),
            '<img src="%s/image" alt="" title="" height="16" width="16" class="image-fullsize" />' % self.folder_url)

    def testCustom(self):
        self.assertEqual(self.image.tag(foobar="baz"),
            '<img src="%s/image" alt="" title="" height="16" width="16" foobar="baz" />' % self.folder_url)

    def testIcon(self):
        self.assertEqual(self.image.tag(icon=1),
            '<img src="%s/image?icon=1" alt="" title="" height="32" width="32" />' % self.folder_url)

    def testPreview(self):
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)
        self.assertEqual(self.image.tag(preview=1),
            '<img src="%s/image?preview=1" alt="" title="" height="10" width="10" />' % self.folder_url)

    def testBorder(self):
        # The border argument is ignored
        self.assertEqual(self.image.tag(border=2),
            '<img src="%s/image" alt="" title="" height="16" width="16" />' % self.folder_url)


class TestPreviewTag(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder_url = self.folder.absolute_url()
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)

    def testDefault(self):
        self.assertEqual(self.image.preview_tag(),
            '<img src="%s/image?preview=1" alt="" title="" height="10" width="10" />' % self.folder_url)

    def testDefaultAlt(self):
        self.image.alt = 'The Image'
        self.assertEqual(self.image.preview_tag(),
            '<img src="%s/image?preview=1" alt="The Image" title="" height="10" width="10" />' % self.folder_url)

    def testDefaultTitle(self):
        self.image.title = 'The Image'
        self.assertEqual(self.image.preview_tag(),
            '<img src="%s/image?preview=1" alt="" title="The Image" height="10" width="10" />' % self.folder_url)

    def testAlt(self):
        self.assertEqual(self.image.preview_tag(alt='The Image'),
            '<img src="%s/image?preview=1" alt="The Image" title="" height="10" width="10" />' % self.folder_url)

    def testAltQuoting(self):
        self.assertEqual(self.image.preview_tag(alt='<The Image>'),
            '<img src="%s/image?preview=1" alt="&lt;The Image&gt;" title="" height="10" width="10" />' % self.folder_url)

    def testTitle(self):
        self.assertEqual(self.image.preview_tag(title='The Image'),
            '<img src="%s/image?preview=1" alt="" title="The Image" height="10" width="10" />' % self.folder_url)

    def testTitleQuoting(self):
        self.assertEqual(self.image.preview_tag(title='The "Image"'),
            '<img src="%s/image?preview=1" alt="" title="The &quot;Image&quot;" height="10" width="10" />' % self.folder_url)

    def testWidthHeight(self):
        self.assertEqual(self.image.preview_tag(width=32, height=32),
            '<img src="%s/image?preview=1" alt="" title="" height="32" width="32" />' % self.folder_url)

    def testScale(self):
        self.assertEqual(self.image.preview_tag(scale=0.5),
            '<img src="%s/image?preview=1" alt="" title="" height="5" width="5" />' % self.folder_url)

    def testCssClass(self):
        self.assertEqual(self.image.preview_tag(css_class="image-preview"),
            '<img src="%s/image?preview=1" alt="" title="" height="10" width="10" class="image-preview" />' % self.folder_url)

    def testCustom(self):
        self.assertEqual(self.image.preview_tag(foobar="baz"),
            '<img src="%s/image?preview=1" alt="" title="" height="10" width="10" foobar="baz" />' % self.folder_url)


class TestRealLifeExamples(ExtFileTestCase):

    def afterSetUp(self):
        ExtFileTestCase.afterSetUp(self)
        self.folder_url = self.folder.absolute_url()
        self.addExtImage(id='image', file=gifImage)
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)

    def testTextLink(self):
        # Render a text link to the image
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)
        self.assertEqual(self.image.link(text='The Image', title='Click for full-size image'),
            '<a href="%s/image" title="Click for full-size image">The Image</a>' % self.folder_url)

    def testPreviewLink(self):
        # Render the preview tag, surrounded by a link to the full-size image
        self.image.manage_create_prev(maxx=10, maxy=10, ratio=1)
        self.assertEqual(self.image.link(text=self.image.preview_tag(), structure=True,
                                         title='Click for full-size image'),
            '<a href="%s/image" title="Click for full-size image">'
            '<img src="%s/image?preview=1" alt="" title="" height="10" width="10" />'
            '</a>' % (self.folder_url, self.folder_url))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtFileLink))
    suite.addTest(makeSuite(TestPreviewLink))
    suite.addTest(makeSuite(TestExtImageTag))
    suite.addTest(makeSuite(TestPreviewTag))
    suite.addTest(makeSuite(TestRealLifeExamples))
    return suite

