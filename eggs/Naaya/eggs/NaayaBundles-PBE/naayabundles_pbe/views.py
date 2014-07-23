from DateTime import DateTime
from Products.Five.browser import BrowserView
from base64 import b64encode
from cPickle import dumps
from lxml.etree import Element
from zope.interface import implements, Interface
import codecs
import lxml.etree
import os


class IObjectExporter(Interface):
    """ Exporter for one object
    """

    def export(root):
        """ Modifies the root node
        """


def name_to_id(s):
    return ''.join([x.capitalize() for x in s.split(' ')])


def build_node(obj):
    name = obj.__class__.__module__ + '.' + obj.__class__.__name__
    return Element(name)


class Exporter(object):
    def __init__(self, context):
        self.context = context


class PersistentObjectExporter(object):
    implements(IObjectExporter)

    def __init__(self, context):
        self.context = context

    def export(self, root=None):
        if root is None:
            root = build_node(self.context)
            root.set('id', self.context.id)

        if not hasattr(self.context, '__dict__'):
            root.text = str(self.context)
            return

        for k, v in vars(self.context).items():
            if hasattr(v, 'objectIds'):     # avoid exporting folderish objects, use export folders for structure
                continue

            el = build_node(v)
            el.set('id', k)
            exporter = IObjectExporter(v)
            exporter.export(root=el)
            root.append(el)

        return root


class FallbackObjectExporter(Exporter):

    def export(self, root):
        try:
            root.text = str(self.context)
        except Exception:
            root.text = b64encode(lxml.etree.CDATA(dumps(self.context)))
            root.set('marshal', 'b64encoded_pickle')


class StringExporter(Exporter):
    def export(self, root):
        try:
            root.text = self.context
        except Exception:
            root.text = b64encode(self.context)
            root.set('marshal', 'b64encoded')


class ListExporter(Exporter):
    def export(self, root):
        for i, val in enumerate(self.context):
            node = build_node(val)
            node.set('id', str(i))
            IObjectExporter(val).export(node)
            root.append(node)


class DictExporter(Exporter):
    def export(self, root):
        for k, val in self.context.items():
            node = build_node(val)
            node.set('id', str(k))
            IObjectExporter(val).export(node)
            root.append(node)


class ExportUpdatedObjects(BrowserView):
    before = 20     # look behind 600 days
    base = "/tmp/export-obj"

    def __call__(self):
        site = self.context.getSite()
        catalog = site.portal_catalog

        if not os.path.exists(self.base):
            os.makedirs(self.base)

        start = DateTime() - self.before
        brains = catalog.searchResults(
            bobobase_modification_time={'query':start, 'range':'min'})
        brains = catalog.searchResults(xx=True)
        print len(brains)

        for brain in brains:
            try:
                ob = brain.getObject()
            except KeyError:    # objects not found
                continue


            fpath = os.path.join(self.base, '/'.join(ob.getPhysicalPath()[1:])) + '.xml'
            base = os.path.dirname(fpath)

            if not os.path.exists(base):
                os.makedirs(base)

            # if ob.id == "library":
            #     import pdb; pdb.set_trace()
            adapter = IObjectExporter(ob)
            root = adapter.export(None)
            f = codecs.open(fpath, 'w', 'utf-8')
            f.write(lxml.etree.tounicode(root, pretty_print=True))
            f.close()

        return "Done"


class ImportUpdatedObjects(BrowserView):
    before = 20     # look behind 600 days
    base = "/tmp/export-obj"

    def __call__(self):
        site = self.context.getSite()
        #catalog = site.portal_catalog


        connection = site._p_jar
        obj = site

        while connection is None:
            obj=obj.aq_parent
            connection=obj._p_jar

        for path, dirs, files in os.walk(self.base):
            for file in files:
                if not file.endswith('zexp'):
                    continue
                fpath = os.path.join(path, file)

                try:
                    ob=connection.importFile(fpath, customImporters=customImporters)
                except:
                    print "Error for", fpath
                else:
                    print "Success for ", fpath

        return "Done"
