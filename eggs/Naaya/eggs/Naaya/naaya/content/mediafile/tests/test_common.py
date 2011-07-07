from naaya.content.base.tests.common import _IconTests
from naaya.content.mediafile.mediafile_item import addNyMediaFile

class MediaFileIconTests(_IconTests):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya Media File')
        kwargs = {'title': 'My mediafile', '_skip_videofile_check': True}
        ob = parent[addNyMediaFile(parent, **kwargs)]
        ob.approveThis()
        return ob
