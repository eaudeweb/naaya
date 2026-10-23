from Testing import ZopeTestCase
ZopeTestCase.installProduct('NaayaPhotoArchive')

def patch_NyPhoto_view():
    """ We need to patch NyPhoto.view because the test publisher doesn't
    know about the IStreamIterator interface """
    from Products.NaayaPhotoArchive.NyPhoto import NyPhoto

    old_view = NyPhoto.view

    def new_view(self, REQUEST, display='', **kwargs):
        """ patch NyPhoto.view to return the whole body """
        ret = old_view(self, REQUEST, display, **kwargs)
        if isinstance(ret, (str, bytes)):
            return ret
        try:
            return b''.join(ret)
        finally:
            if hasattr(ret, 'close'):
                ret.close()

    NyPhoto.view = new_view

patch_NyPhoto_view()
