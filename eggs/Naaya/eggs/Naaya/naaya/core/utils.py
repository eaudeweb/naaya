def relative_object_path(obj, ancestor):
    """
    Compute the relative path from `ancestor` to `obj` (`obj` must be
    somewhere inside `ancestor`)
    """

    ancestor_path = '/'.join(ancestor.getPhysicalPath())
    obj_path = '/'.join(obj.getPhysicalPath())

    if not obj_path.startswith(ancestor_path):
        raise ValueError('My path is not in the site. Panicking.')
    return obj_path[len(ancestor_path)+1:]
