import logging

from ZPublisher.BeforeTraverse import rewriteBeforeTraverse

from naaya.core.site_logging import create_site_logger


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

def site_cloned(site, event):
    """If a `INySite` was pasted check the `__before_traverse__` for
    old object's values and delete them.

    For example::

        >>> portal.__before_traverse__
            {
                (99, 'Localizer'):
                    <ZPublisher.BeforeTraverse.NameCaller>,
                (99, 'Naaya Site/copy_of_portal'):
                    <ZPublisher.BeforeTraverse.NameCaller>,
                (99, 'Naaya Site/portal'):
                    <ZPublisher.BeforeTraverse.NameCaller>
            }

    From the above example the last value (original object) in the dict should
    be removed because the before_traverse hooks will use that instead of
    new object's value.

    """
    btr = {}
    for name, ob in site.__before_traverse__.items():
        # Check if it is of the same content type
        if site.meta_type in name[1]:
            # Leave the current object and remove the old one
            if ("%s/%s" % (site.meta_type, site.id) ==
                name[1]):
                btr[name] = ob
        else:
            btr[name] = ob
    #Override __before_traverse__
    rewriteBeforeTraverse(site, btr)

def site_moved_or_added(site, event):
    """
    Handler triggered after a site was added to a location as a consequence of
    a moval or of an initialization of a new one

    """
    create_site_logger(site)

def zope_started(event):
    """ Handling IProcessStarting Event """
    zlog = logging.getLogger("Zope")
    from asyncore import socket_map
    for server in socket_map.values():
        if server.addr:
            host, port = server.addr
            if host in ('127.0.0.1', '0.0.0.0'):
                host = 'localhost'
            zlog.info("Instance available on http://%s:%d", host, port)
            return
