"""
This is not exactly a CIRCA related feature, but it is used in EIONET
Forum to move data from Archives instance to Forum/Projects.

"""
import re
import transaction


def manage_main_catch_path(self, REQUEST, manage_tabs_message, title):
    """
    Unfortunately ObjectManager.manage_exportObject does not return a value.
    We have to pretend we have request and mock the manage_main call
    to get the path of the zexp on server.

    """
    pattern = r'<em>(.*?)</em> successfully exported to <em>(.*?)</em>'
    path = re.match(pattern, manage_tabs_message)
    if not path:
        raise ValueError("Can not deduct zexp path from ZMI message")
    return path.groups()[1]

def write_zexp(ob):
    """ Generates corresponding zexp file of `ob` and any objects under it """
    sp = transaction.savepoint()
    try:
        ob.manage_main = manage_main_catch_path
        path_on_disk = ob.manage_exportObject(REQUEST=True)
    finally:
        sp.rollback()
    return path_on_disk

def load_zexp(zexp_path, destination):
    """ Given the zexp file, it loads the data in the given OFS destination """
    destination._importObjectFromFile(zexp_path, verify=0, set_owner=0)
