from Testing import ZopeTestCase
ZopeTestCase.installProduct('NaayaPhotoArchive')

def patch_NyPhoto_view():
    """ We need to patch NyPhoto.view because the test publisher doesn't
    know about the IStreamIterator interface """
    from Products.NaayaPhotoArchive.NyPhoto import NyPhoto
    from Products.ExtFile.ExtFile import stream_iterator
    from StringIO import StringIO

    old_view = NyPhoto.view

    def new_view(self, REQUEST, display='', **kwargs):
        """ patch NyPhoto.view to always return a str """
        ret = old_view(self, REQUEST, display, **kwargs)
        if isinstance(ret, str):
            return ret
        else:
            output = StringIO()
            try:
                while True:
                    output.write(ret.next())
            except StopIteration:
                pass
            return output.getvalue()

    NyPhoto.view = new_view

patch_NyPhoto_view()
