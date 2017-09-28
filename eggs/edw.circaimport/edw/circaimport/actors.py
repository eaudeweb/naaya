import logging
import mimetypes
logger = logging.getLogger('edw.circaimport.ui')

class DemoActor(object):
    def __init__(self):
        self.count = {'files': 0, 'folders': 0, 'urls': 0}

    def folder_entry(self, parent_path, folder_id,
                     title, description, date, userid):
        pass #print 'folder %r (%r, %s)' % (folder_id, userid, date)
        self.count['folders'] += 1

    def document_entry(self, parent_path, ob_id, filename, data_file,
                       title, description, keywords, date, userid):
        pass #print ('document %r (%r, %s)' % (title, userid, date))
        self.count['files'] += 1

    def url_entry(self, parent_path, ob_id, filename, url,
                  title, description, keywords, date, userid):
        pass #print ('url %r (%r, %s)' % (title, userid, date))
        self.count['urls'] += 1

    def warn(self, msg):
        print "WARNING: %s" % msg

    def finished(self):
        print 'done:', repr(self.count)

try:
    from datetime import datetime
    from Products.Naaya.NyFolder import addNyFolder
    from naaya.core.zope2util import path_in_site
    from naaya.content.url.url_item import addNyURL
    from naaya.content.bfile.bfile_item import addNyBFile, make_blobfile
except ImportError:
    with_naaya = False
else:
    with_naaya = True

def nydateformat(date):
    return date.strftime('%d/%m/%Y')

def get_parent(context, parent_path):
    if parent_path in (None, ''):
        return context
    else:
        return context.restrictedTraverse(parent_path)

def join_parent_path(parent_path, ob_id):
    if parent_path:
        return parent_path + '/' + ob_id
    else:
        return ob_id

class ZopeActor(object):
    def __init__(self, context, default_userid=''):
        assert with_naaya
        self.context = context
        self.count = {'files': 0, 'folders': 0, 'urls': 0}
        self.rename = {}
        self.default_userid = default_userid

    def folder_entry(self, parent_path, folder_id,
                     title, description, date, userid):

        parent = get_parent(self.context, parent_path)
        kwargs = {
            'id': folder_id,
            'contributor': userid or self.default_userid,
            'releasedate': nydateformat(date),
            'title': title,
            'description': description,
            '_send_notifications': False,
        }
        new_folder_id = addNyFolder(parent, **kwargs)
        new_folder = parent[new_folder_id]
        logger.info("Added folder: %r", path_in_site(new_folder))
        self.count['folders'] += 1

    def document_entry(self, parent_path, ob_id, filename, data_file,
                       title, description, keywords, date, userid):
        from StringIO import StringIO
        assert isinstance(data_file, StringIO)
        data_file.filename = filename
        content_type, content_encoding = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = 'application/octet-stream'
        bf = make_blobfile(data_file,
                           content_type=content_type,
                           removed=False,
                           timestamp=datetime(date.year, date.month, date.day))

        parent = get_parent(self.context, parent_path)
        orig_path = join_parent_path(parent_path, ob_id)

        if orig_path in self.rename:
            ob_path = self.rename.get(orig_path)
            the_file = self.context.restrictedTraverse(ob_path)
            logger.warn('new document version for %r' % orig_path)
            if keywords or description:
                logger.warn('ignoring keywords=%r, description=%r' %
                          (keywords, description))

        else:
            kwargs = {
                'id': ob_id,
                'contributor': userid or self.default_userid,
                'releasedate': nydateformat(date),
                'title': title,
                'description': description,
                'keywords': keywords,
                '_send_notifications': False,
            }
            assert ob_id not in parent.objectIds()
            the_file_id = addNyBFile(parent, **kwargs)
            if parent_path:
                self.rename[orig_path] = parent_path + '/' + the_file_id
            else:
                self.rename[orig_path] = the_file_id
            the_file = parent[the_file_id]

        the_file._versions.append(bf)
        logger.info("Added file: %r", path_in_site(the_file))
        self.count['files'] += 1

    def url_entry(self, parent_path, ob_id, filename, url,
                  title, description, keywords, date, userid):
        parent = get_parent(self.context, parent_path)
        orig_path = join_parent_path(parent_path, ob_id)

        assert orig_path not in self.rename

        kwargs = {
            'id': ob_id,
            'contributor': userid or self.default_userid,
            'releasedate': nydateformat(date),
            'title': title,
            'description': description,
            'keywords': keywords,
            'locator': url,
            '_send_notifications': False,
        }
        url_id = addNyURL(parent, **kwargs)
        if parent_path:
            self.rename[orig_path] = parent_path + '/' + url_id
        else:
            self.rename[orig_path] = url_id
        new_url = parent[url_id]
        logger.info("Added url: %r", path_in_site(new_url))
        self.count['urls'] += 1

    def warn(self, msg):
        logger.warn(msg)

    def finished(self):
        logger.debug('done: %s', repr(self.count))
