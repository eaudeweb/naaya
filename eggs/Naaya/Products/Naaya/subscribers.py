def update_maintopics_after_move(event):
    """ object was renamed; update maintopics """
    site = event.context.getSite()
    mt = site.maintopics
    old_sp = event.old_site_path
    new_sp = event.new_site_path

    # maybe the folder is listed with its site path
    if old_sp in mt:
        mt[mt.index(old_sp)] = new_sp
        site._p_changed = True

    # or maybe with its physical path
    prefix = '/'.join(site.getPhysicalPath()[1:]) + '/'
    if prefix + old_sp in mt:
        mt[mt.index(prefix + old_sp)] = prefix + new_sp
        site._p_changed = True
