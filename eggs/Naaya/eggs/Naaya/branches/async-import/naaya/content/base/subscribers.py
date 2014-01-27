from naaya.core.site_logging import log_user_access


def log_view_event(event):
    """ Log view action on object """
    log_user_access(event.context, event.user_id, 'VIEW')

def log_download_event(event):
    """ Log download action on object """
    log_user_access(event.context, event.user_id, 'DOWNLOAD')
