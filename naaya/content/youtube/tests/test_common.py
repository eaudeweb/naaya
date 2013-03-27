from naaya.content.base.tests.common import _IconTests
from naaya.content.youtube.youtube_item import addNyYoutube

class YoutubeIconTests(_IconTests):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya Youtube')
        ob = parent[addNyYoutube(parent, title='My Youtube video',
            youtube_id='uelHwf8o7_U', iframe_width='640', iframe_height='360')]
        ob.approveThis()
        return ob
