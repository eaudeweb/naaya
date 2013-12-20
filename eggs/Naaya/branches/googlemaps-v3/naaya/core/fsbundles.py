import os
import logging
import ConfigParser
from zope.component import getGlobalSiteManager
from zope.interface import implements
from naaya.component import bundles
from naaya.component.interfaces import IBundleReloader
from Products.NaayaCore.FormsTool.bundlesupport import \
        register_templates_in_directory, FilesystemTemplateWriter
from Products.Naaya.interfaces import INySite
from interfaces import IFilesystemBundleFactory


log = logging.getLogger(__name__)


class FilesystemBundleLoader(object):
    """ Load the components of a bundle from the filesystem. """

    implements(IBundleReloader)

    def __init__(self, bundle_name, bundle_path):
        self.bundle_name = bundle_name
        self.bundle_path = bundle_path

    @property
    def templates_path(self):
        return os.path.join(self.bundle_path, 'templates')

    def load_all(self):
        # TODO flush the templates first
        register_templates_in_directory(self.templates_path, self.bundle_name)

    def reload_bundle(self):
        log.info("Bundle %r reloaded", self.bundle_name)
        self.load_all()


def register_bundle_factory(bundles_dir, name_prefix, parent_name):
    #from zope.interface import implementer
    #@implementer(IFilesystemBundleFactory)
    def filesystem_bundle_factory(site):
        def create_bundle():
            """ Create a writable bundle on demand. """
            site_path = site.getPhysicalPath()
            if site_path[0] == '': # remove first empty path
                site_path = site_path[1:]
            bundle_name = name_prefix + '-'.join(site_path)

            site_parent = get_site_parent(site)
            parent_bundle = bundles.get(parent_name)
            if site_parent is not parent_bundle:
                raise ValueError("Site has wrong parent, %r != %r" %
                                 (site_parent, parent_bundle))
            bundle_path = os.path.join(bundles_dir, bundle_name + ".bundle")
            log.info("Creating bundle %r at %r", bundle_name, bundle_path)
            try:
                os.makedirs(bundle_path)
            except OSError, e:
                raise ValueError("Filesystem bundle %r already exists (%s)" %
                                 (bundle_name, e))

            cfg_file = open(os.path.join(bundle_path, 'bundle.cfg'), 'wb')
            cfg_file.write("[bundle]\nparent-bundle = %s\n" % parent_name)
            cfg_file.close()

            # TODO in ZEO configurations we need to notify the other instances
            load_filesystem_bundle(bundle_path, bundle_name, parent_name)
            new_bundle = bundles.get(bundle_name)
            site.set_bundle(new_bundle)
            return new_bundle

        return create_bundle


    gsm = getGlobalSiteManager()
    gsm.registerAdapter(filesystem_bundle_factory,
                        (INySite,), IFilesystemBundleFactory, name=parent_name)
    log.info("Filesystem bundles %r will be created under %r",
             name_prefix, bundles_dir)

def get_site_parent(site):
    lsm = site.getSiteManager()
    return lsm.__bases__[0]

def get_writable_bundle(site):
    """ Look for a server bundle where templates can be written to disk. """
    from Products.NaayaCore.FormsTool.interfaces import IFilesystemTemplateWriter

    # TODO formalize this logic as a "parent_bundles" generator
    gsm = getGlobalSiteManager()
    bundle = site.get_bundle()
    from naaya.component.interfaces import IBundle
    while IBundle.providedBy(bundle):
        writer = gsm.queryUtility(IFilesystemTemplateWriter,
                                  name=bundle.__name__)
        if writer is not None:
            return bundle
        bundle = bundle.__bases__[0]
    else:
        return None


def get_filesystem_bundle_factory(site):
    """ Convenienve function to look up a filesystem bundle factory. """
    gsm = getGlobalSiteManager()
    site_parent = get_site_parent(site)
    return gsm.queryAdapter(site, IFilesystemBundleFactory,
                            name=site_parent.__name__)


def _read_bundle_cfg(bundle_path):
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(bundle_path, 'bundle.cfg'))
    if not config.has_section('bundle'):
        config.add_section('bundle')
    return config

def load_filesystem_bundle(bundle_path, bundle_name, default_parent_name=None):
    """
    Load a bundle from the filesystem:

    * register its components
    * regiser a writer, if writing is allowed
    * register a reloader

    :param bundle_path: Path to bundle folder that contains a
                        "templates" sub-folder.
    :param bundle_name: Name of the bundle where registration will
                        happen.
    :param default_parent_name: Name of the parent bundle to set on the
                                loaded bundle, if no parent is defined in
                                the `bundle.cfg` file.
    """
    gsm = getGlobalSiteManager()

    cfg = _read_bundle_cfg(bundle_path)
    try:
        parent_name = cfg.get('bundle', 'parent-bundle')
    except ConfigParser.NoOptionError:
        parent_name = default_parent_name

    bundle = bundles.get(bundle_name)
    if parent_name is not None:
        bundle.set_parent(bundles.get(parent_name))

    loader = FilesystemBundleLoader(bundle_name, bundle_path)
    loader.load_all()
    gsm.registerUtility(loader, name=bundle_name)

    writer = FilesystemTemplateWriter(loader.templates_path)
    gsm.registerUtility(writer, name=bundle_name)


def auto_bundle_package(bundles_dir, name_prefix, parent_name):
    names = set()
    for item_name in os.listdir(bundles_dir):
        name, ext = os.path.splitext(item_name)
        if ext != '.bundle':
            continue
        bundle_path = os.path.join(bundles_dir, item_name)
        load_filesystem_bundle(bundle_path, name, parent_name)
        names.add(name)

    if names:
        log.info("Loaded %r from %r", sorted(names), bundles_dir)

    if True: # TODO check that some config variable was set
        register_bundle_factory(bundles_dir, name_prefix, parent_name)
