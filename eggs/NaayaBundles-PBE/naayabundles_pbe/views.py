from DateTime import DateTime
from Products.Five.browser import BrowserView
#from ZODB.POSException import POSKeyError
from cPickle import dumps
from zope.interface import implements, Interface
import codecs
import lxml.etree
import os


class IObjectExporter(Interface):
    """ Exporter for one object
    """

    def etree():
        """ Return the etree representation of this element
        """

def name_to_id(s):
    return ''.join([x.capitalize() for x in s.split(' ')])


class GenericObjectExporter(object):
    implements(IObjectExporter)

    def __init__(self, context):
        self.context = context

    def export(self, root=None, name=None):
        if root is None:
            if name is None:
                name = name_to_id(self.context.meta_type)
            root = lxml.etree.Element(name)
            root.set('type', self.context.__class__.__name__)

        if self.context is None:
            NoneTypeExporter(self.context).export(root, name)   # Can't adapt again to None
            return

        if not hasattr(self.context, '__dict__'):
            BasicObjectExporter(self.context).export(root, name)
            return

        for k, v in vars(self.context).items():
            if hasattr(v, 'objectIds'):
                continue            # don't export folderish objects
            if k.startswith('_'):   # don't export private attributes
                continue

            if k.startswith('.'):
                print "skipping",k, v, self.context
                continue

            el = lxml.etree.Element(k)
            el.set('type', v.__class__.__name__)
            exporter = IObjectExporter(v)
            exporter.export(root=el, name=k)
            root.append(el)

        return root


class BasicObjectExporter(object):
    def __init__(self, value):
        self.value = value

    def export(self, root, name):
        el = lxml.etree.Element(name)
        el.set('type', self.value.__class__.__name__)
        try:
            el.text = str(self.value)
        except Exception, e:
            print "exception for", name, e
            el.text = lxml.etree.CDATA(dumps(self.value))

        root.append(el)


class StringExporter(object):
    def __init__(self, value):
        self.value = value

    def export(self, root, name):
        # el = lxml.etree.Element(name)
        # el.set('type', self.value.__class__.__name__)
        # el.text = self.value
        root.text = self.value

        #root.append(el)


class ListExporter(object):
    def __init__(self, value):
        self.value = value

    def export(self, root, name):
        el = lxml.etree.Element(name)
        el.set('type', self.value.__class__.__name__)
        for val in self.value:
            IObjectExporter(val).export(el, name='entry')
        root.append(el)


class TupleExporter(ListExporter):
    pass


class IntExporter(object):
    def __init__(self, value):
        self.value = value

    def export(self, root, name):
        el = lxml.etree.Element(name)
        el.set('type', self.value.__class__.__name__)
        el.text = str(self.value)
        root.append(el)


class NoneTypeExporter(object):
    def __init__(self, value):
        self.value = value

    def export(self, root, name):
        el = lxml.etree.Element(name)
        el.set('type', self.value.__class__.__name__)
        el.text = str(self.value)
        root.append(el)


class DictExporter(object):
    def __init__(self, value):
        self.value = value

    def export(self, root, name):
        el = lxml.etree.Element(name)
        el.set('type', self.value.__class__.__name__)
        for k, v in self.value.items():
            IObjectExporter(v).export(el, name=k)
        root.append(el)


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

            if ob.id == "library":
                import pdb; pdb.set_trace()
            adapter = IObjectExporter(ob)
            root = adapter.export()
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
