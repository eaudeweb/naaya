import logging

from naaya.content.pointer.constants import META_TYPE_NAAYA_POINTER

logger = logging.getLogger(__name__)

def handle_cut_paste_content(event):
    """ Update pointers when object is moved """
    obj = event.context
    site = obj.getSite()
    old_site_path = event.old_site_path
    new_site_path = event.new_site_path
    cat = site.getCatalogTool()
    if 'pointer' not in cat.indexes():
        return # we require 'pointer' FieldIndex
    pointer_brains = cat.search({'meta_type': META_TYPE_NAAYA_POINTER,
                                 'pointer': old_site_path})
    need_recataloging = []
    for brain in pointer_brains:
        try:
            pointer = brain.getObject()
            pointer.pointer = new_site_path
        except Exception:
            logger.exception(("Can not reassign pointer %s on move event of "
                              "object %s to %s, maybe catalog needs rebuilt?"),
                             brain.path, old_site_path, new_site_path)
        else:
            need_recataloging.append(pointer)

    for pointer in need_recataloging:
        site.recatalogNyObject(pointer)
