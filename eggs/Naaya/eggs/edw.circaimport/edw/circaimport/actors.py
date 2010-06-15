class DemoActor(object):
    def __init__(self):
        self.count = {'files': 0, 'folders': 0, 'urls': 0}

    def folder_entry(self, parent_path, folder_id,
                     title, description, date, userid):
        pass #print 'folder %r (%r, %s)' % (folder_id, userid, date)
        self.count['folders'] += 1

    def document_entry(self, parent_path, ob_id, filename, data_file,
                       title, description, date, userid):
        pass #print ('document %r (%r, %s)' % (title, userid, date))
        self.count['files'] += 1

    def url_entry(self, parent_path, ob_id, filename, url,
                  title, description, date, userid):
        pass #print ('url %r (%r, %s)' % (title, userid, date))
        self.count['urls'] += 1

    def warn(self, msg):
        print "WARNING: %s" % msg

    def finished(self):
        print 'done:', repr(self.count)

try:
    from datetime import datetime
    from Products.Naaya.NyFolder import addNyFolder
    from naaya.core.utils import path_in_site
    from naaya.core.utils import mimetype_from_filename
    from naaya.content.url.url_item import addNyURL
    from naaya.content.bfile.bfile_item import addNyBFile, make_blobfile
except ImportError:
    with_naaya = False
else:
    with_naaya = True

def nydateformat(date):
    return date.strftime('%d/%m/%Y')

def get_parent(context, parent_path):
    if parent_path is None:
        return context
    else:
        return context.restrictedTraverse(parent_path)

class ZopeActor(object):
    def __init__(self, context, report):
        assert with_naaya
        self.context = context
        self.report = report
        self.count = {'files': 0, 'folders': 0, 'urls': 0}
        self.rename = {}

    def folder_entry(self, parent_path, folder_id,
                     title, description, date, userid):

        parent = get_parent(self.context, parent_path)
        kwargs = {
            'id': folder_id,
            'contributor': userid,
            'releasedate': nydateformat(date),
            'title': title,
            'description': description,
            '_send_notifications': False,
        }
        new_folder_id = addNyFolder(parent, **kwargs)
        new_folder = parent[new_folder_id]
        #print>>self.report, "folder: %r" % path_in_site(new_folder)
        self.count['folders'] += 1

    def document_entry(self, parent_path, ob_id, filename, data_file,
                       title, description, date, userid):
        from StringIO import StringIO
        assert isinstance(data_file, StringIO)
        data_file.filename = filename
        bf = make_blobfile(data_file,
                           content_type=mimetype_from_filename(filename),
                           removed=False,
                           timestamp=datetime(date.year, date.month, date.day))

        parent = get_parent(self.context, parent_path)
        orig_path = parent_path + '/' + ob_id

        if orig_path in self.rename:
            ob_path = self.rename.get(orig_path)
            the_file = self.context.restrictedTraverse(ob_path)

        else:
            kwargs = {
                'id': ob_id,
                'contributor': userid,
                'releasedate': nydateformat(date),
                'title': title,
                'description': description,
                '_send_notifications': False,
            }
            assert ob_id not in parent.objectIds()
            the_file_id = addNyBFile(parent, **kwargs)
            self.rename[orig_path] = parent_path + '/' + the_file_id
            the_file = parent[the_file_id]

        the_file._versions.append(bf)
        #print>>self.report, "file: %r" % path_in_site(the_file)
        self.count['files'] += 1

    def url_entry(self, parent_path, ob_id, filename, url,
                  title, description, date, userid):
        parent = get_parent(self.context, parent_path)
        orig_path = parent_path + '/' + ob_id

        assert orig_path not in self.rename

        kwargs = {
            'contributor': userid,
            'releasedate': nydateformat(date),
            'title': title,
            'description': description,
            'locator': url,
            '_send_notifications': False,
        }
        new_url_id = addNyURL(parent, **kwargs)
        self.rename[orig_path] = parent_path + '/' + new_url_id
        new_url = parent[new_url_id]
        #print>>self.report, "url: %r" % path_in_site(new_url)
        self.count['urls'] += 1

    def warn(self, msg):
        print>>self.report, "WARN: %s" % msg

    def finished(self):
        print>>self.report, 'done:', repr(self.count)
