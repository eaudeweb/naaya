import os
import logging
from zope.interface import implements
from interfaces import IFilesystemTemplateWriter


log = logging.getLogger(__name__)


def register_templates_in_directory(templates_path, bundle_name):
    """ Register all templates found in a folder. """

    from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

    if not os.path.isdir(templates_path):
        return

    count = 0
    for filename in os.listdir(templates_path):
        fileroot, ext = os.path.splitext(filename)
        if ext in ('.zpt', '.pt', ):
            tmpl_path = os.path.join(templates_path, filename)
            NaayaPageTemplateFile(tmpl_path, globals(), fileroot, bundle_name)
            count += 1

    if count:
        log.debug("Loaded %d templates from %r into bundle %r",
                  count, templates_path, bundle_name)


class FilesystemTemplateWriter(object):
    implements(IFilesystemTemplateWriter)

    def __init__(self, templates_path):
        self.templates_path = templates_path

    def write_zpt(self, name, content):
        if not os.path.isdir(self.templates_path):
            os.makedirs(self.templates_path)

        if isinstance(content, unicode):
            content = content.encode('utf-8')
        f = open(os.path.join(self.templates_path, name+'.zpt'), 'wb')
        f.write(content)
        f.close()
