""" Utility functions for zope folders """

def sort_folder(folder_ob, object_ids):
    """ Given a folder object and a list of object ids, reorder that folder.
    It also works with a partial ordering. Not all ids in the folder must be
    specified in order for this to work, however the ids that are not present
    will be put at the end of the folder.

    """
    ordered_objects = []
    unordered_objects = []
    #Construct a list of unordered objects (those that not present in object_ids)
    for ob_data in folder_ob._objects:
        if ob_data['id'] not in object_ids:
            unordered_objects.append(ob_data)
    #Build a list of ordered objects
    for ob_id in object_ids:
        for ob_data in folder_ob._objects:
            if ob_data['id'] == ob_id:
                ordered_objects.append(ob_data)
                break

    # avoid unnecessary commits (order maintained)
    desired_order = tuple(ordered_objects + unordered_objects)
    if folder_ob._objects != desired_order:
        folder_ob._objects = desired_order
