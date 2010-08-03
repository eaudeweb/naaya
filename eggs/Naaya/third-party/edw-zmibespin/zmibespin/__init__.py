import os

from App.ImageFile import ImageFile
from App.Management import Navigation

class ServeStaticFolder(object):
    """ """
    def __init__(self, path, file=''):
        """ """
        self.path = path
        self.file = file
    def __bobo_traverse__(self, REQUEST, name):
        """ Internal Zope resolve method """
        return ServeStaticFolder(self.path + '/' + name, self.file)

    def __call__(self, REQUEST=None):
        """ """
        try:
            return ImageFile(self.path + self.file, globals()).index_html(
                REQUEST, REQUEST.RESPONSE)
        except IOError:
            REQUEST.RESPONSE.setStatus(404)
            return "Not Found"

#Monkey-patching (Add /bespin to app)
#Navigation.security.declarePublic('bespin') - we don't really care about sec
setattr(Navigation, 'bespin', ServeStaticFolder('www'))

#Patching zmi header to add the necesary scripts
zmipatch_content = open(os.path.dirname(__file__) + '/www/zmi.dtml', 'r').read()
manage_page_header = getattr(Navigation, 'manage_page_header')
#Couldn't find any sane way to do this.. thanks DTML
manage_page_header.edited_source = manage_page_header.read().replace('</head>',
        zmipatch_content + "\n</head>")
manage_page_header._v_cooked=manage_page_header.cook()
