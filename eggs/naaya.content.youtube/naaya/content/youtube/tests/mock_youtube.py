import urllib.error
from unittest import mock

from naaya.content.youtube import youtube_item

EXISTING_VIDEOS = ('uelHwf8o7_U', 'dQw4w9WgXcQ')


def fake_urlopen(url, *args, **kwargs):
    """ Answer like the YouTube oembed API without network access """
    if url.split('v=')[-1] not in EXISTING_VIDEOS:
        raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)
    return mock.MagicMock()


def patch_youtube():
    """ Patch the oembed request made by checkExistingVideo """
    return mock.patch.object(youtube_item.urllib.request, 'urlopen',
                             side_effect=fake_urlopen)


class YoutubeMockMixin(object):
    """ Patch youtube.com for each test """

    def setUp(self):
        patcher = patch_youtube()
        self.urlopen = patcher.start()
        self.addCleanup(patcher.stop)
        super(YoutubeMockMixin, self).setUp()
