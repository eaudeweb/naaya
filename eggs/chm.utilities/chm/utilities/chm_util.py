import re
from Globals import InitializeClass
from naaya.core.zope2util import RestrictedToolkit

def monkey_patch_rstk():
    def parse_twitter_message(self, msg):
        """ parse the @, # and links from a twitter message """
        #strip the "<username>: " that preceeds all twitter feed entries
        text = re.sub(r'^\w+:\s', '', msg)

        #parse links
        text = re.sub(
            r"[^\"](http://(\w|\.|/|\?|=|%|&)+)",
            lambda x: "<a href='%s'>%s</a>" % (x.group(), x.group()),
            text)

        #parse @tweeter
        text = re.sub(
            r'@(\w+)',
            lambda x: "<a href='http://twitter.com/%s'>%s</a>"\
                 % (x.group()[1:], x.group()),
            text)

        #parse #hashtag
        text = re.sub(
            r'#(\w+)',
            lambda x: "<a href='http://twitter.com/search?q=%%23%s'>%s</a>"\
                 % (x.group()[1:], x.group()),
            text)

        return text

    RestrictedToolkit.parse_twitter_message = parse_twitter_message
    InitializeClass(RestrictedToolkit)