from DateTime import DateTime
from Products.Five.browser import BrowserView
from base64 import b64encode
from cPickle import dumps
from lxml.etree import Element
from zope.interface import implements, Interface
import codecs
import logging
import lxml.etree
import os


log = logging.getLogger("SiteExporter")


class IObjectExporter(Interface):
    """ Exporter for one object
    """

    def export(root):
        """ Modifies the root node
        """


def name_to_id(s):
    return ''.join([x.capitalize() for x in s.split(' ')])


def build_node(obj):
    #obj may be a class in itself
    klass = getattr(obj, '__class__', obj)
    name = klass.__name__
    if klass.__module__ != '__builtin__':
        name = klass.__module__ + '.' + name
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
            cid = self.context.id
            if callable(cid):
                cid = cid()
            root.set('id', cid)

        if not hasattr(self.context, '__dict__'):
            root.text = str(self.context)
            return

        if hasattr(self.context, 'bobobase_modification_time'):
            bbmt = self.context.bobobase_modification_time
            if callable(bbmt):
                bbmt = bbmt()
            root.set('bobobase_modification_time', str(bbmt))

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
        if isinstance(self.context, unicode):
            self.context = self.context.encode('utf-8-sig')
        try:
            root.text = self.context
        except Exception:
            root.text = b64encode(self.context)


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
    base = "/tmp/export-obj"

    def export(self, site):
        log.info("Export site: %s", site.absolute_url())
        catalog = site.portal_catalog

        if not os.path.exists(self.base):
            os.makedirs(self.base)

        before = self.request.form.get("before")
        if before:
            before = int(before)
            start = DateTime() - before
            brains = catalog.searchResults(
                bobobase_modification_time={'query':start, 'range':'min'})
        else:
            # makes catalog return all objects
            brains = catalog.searchResults(invalid=True)

        for brain in brains:
            try:
                ob = brain.getObject()
            except KeyError:    # objects not found
                continue

            fpath = os.path.join(self.base, '/'.join(ob.getPhysicalPath()[1:])) + '.xml'
            base = os.path.dirname(fpath)

            if not os.path.exists(base):
                os.makedirs(base)

            adapter = IObjectExporter(ob)
            root = adapter.export(None)
            f = codecs.open(fpath, 'w', 'utf-8')
            f.write(lxml.etree.tounicode(root, pretty_print=True))
            f.close()

    def __call__(self):
        for obj in self.context.objectValues():
            if not hasattr(obj, 'portal_catalog'):
                continue
            self.export(obj)
            log.info("Export done")
            return "Done"


class UpdateModificationDates(BrowserView):
    base = "/tmp/export-obj"

    def __call__(self):
        site = self.context.getSite()
        catalog = site.portal_catalog

        brains = catalog.searchResults(invalid=True)
        print "Got ", len(brains)
        for brain in brains:
            obj = brain.getObject()
            if hasattr(obj.aq_inner.aq_self, 'last_modification'):
                continue
            path = os.path.join(self.base, brain.getPath()[1:]) + '.xml'
            e = lxml.etree.parse(path)
            try:
                date = e.getroot().get('bobobase_modification_time')
            except:
                print "Couldn't get a date for", obj
                continue
            obj.last_modification = DateTime(date)
            print "Fixed", brain.getPath()

        return "Done"


def import_string(node):
    return node.text

def import_dict(node):
    d = {}
    for child in node.iterchildren():
        d[child.get('id')] = importer(child)
    return d

def import_tuple(node):
    r = ()
    for child in node.iterchildren():
        r += (importer(child),)
    return r

def import_list(node):
    r = []
    for child in node.iterchildren():
        r += (importer(child),)
    return r

def importer(node):
    return importers[node.tag](node)


importers = {
    'str':   import_string,
    'tuple': import_tuple,
    'dict':  import_dict,
    'list':  import_list,
}


class UpdateLocalPropertiesMetadata(BrowserView):
    base = "/tmp/export-obj"

    def __call__(self):
        site = self.context.getSite()
        catalog = site.portal_catalog

        brains = catalog.searchResults(invalid=True)
        for brain in brains:
            obj = brain.getObject()
            if hasattr(obj.aq_inner.aq_self, '_local_properties_metadata'):
                continue
            path = os.path.join(self.base, brain.getPath()[1:]) + '.xml'
            e = lxml.etree.parse(path)
            root = e.getroot()
            meta = root.xpath("//*[@id='_local_properties_metadata']")[0]
            value = importer(meta)
            log.info("Fixing %s to %r", brain.getPath(), value)
            obj._local_properties_metadata = value

        return "Done"
