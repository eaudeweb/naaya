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

def get_noaq_attr(obj, attr, default):
    """
    Return the wanted attribute without
    checking the acquisition tree or `default`.
    """
    return getattr(obj.aq_base, attr, default)

def call_method(obj, attr, default):
    """
    Return the result of calling `obj`s `attr`
    or `default` if `obj` doesn't have `attr`.
    """
    if get_noaq_attr(obj, attr, default) != default:
        return obj[attr]()
    else:
        return default
