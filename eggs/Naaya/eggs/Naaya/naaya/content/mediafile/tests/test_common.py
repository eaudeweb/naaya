from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.mediafile.mediafile_item import addNyMediaFile

class MediaFileCommonTest(_CommonContentTest):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya Media File')
        kwargs = {'title': 'My mediafile', '_skip_videofile_check': True}
        ob = parent[addNyMediaFile(parent, **kwargs)]
        ob.approveThis()
        return ob
