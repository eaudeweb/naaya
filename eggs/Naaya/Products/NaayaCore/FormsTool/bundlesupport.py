import os
import logging


log = logging.getLogger(__name__)


def register_templates_in_directory(templates_path, bundle_name):
    """ Register all templates found in a folder. """

    from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

    count = 0
    for filename in os.listdir(templates_path):
        fileroot, ext = os.path.splitext(filename)
        if ext in ('.zpt', '.pt', ):
            tmpl_path = os.path.join(templates_path, fileroot)
            NaayaPageTemplateFile(tmpl_path, globals(), fileroot, bundle_name)
            count += 1

    if count:
        log.debug("Loaded %d templates from %r into bundle %r",
                  count, templates_path, bundle_name)
