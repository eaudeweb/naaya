from Products.Five.browser import BrowserView

class ReportUnusedFiles(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        app = self.context
        conn = app._p_jar
        db = conn.db()
        storage = db._storage
        oids = storage._index.keys()
        reader = conn._reader
        out = []
        for oid in oids:
            obj = reader.load_oid(oid)
            if 'extfile' in obj.__class__.__name__.lower():
                if not hasattr(obj, 'filename'):
                    continue        # can be naaya.content.file.file_item.NyFile_extfile
                path = '/'.join(obj.filename)
                if path:
                    print path
                    out.append(path)

        with open('/tmp/files.txt', 'w') as f:
            f.write("\n".join(out))

        return "Done"
