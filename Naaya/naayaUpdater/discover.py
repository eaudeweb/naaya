import os, re

def import_name(name):
    # the last __import__ parameter is a hack
    # not sure why it does not work without it on zope products
    return __import__(name, globals(), locals(), [''])

def get_module_dir(module):
    return os.path.dirname(module.__file__)

def get_module_names_for_dir(dir, pattern):
    ret = []
    for f in os.listdir(dir):
        module_name, ext = os.path.splitext(f)
        if ext == '.py' and re.match(pattern, module_name):
            ret.append(module_name)
    return ret

def get_module_names(package_name, pattern):
    package = import_name(package_name)
    package_path = get_module_dir(package)

    module_names = get_module_names_for_dir(package_path, pattern)
    return [package_name + '.' + module_name for module_name in module_names]

def get_module_objects(module_name):
    module = import_name(module_name)
    names = dir(module)

    # remove objects builtin functions
    built_in_list = ['__builtins__', '__doc__', '__file__', '__name__']
    for b in built_in_list:
        if b in names:
            names.remove(b)

    return [getattr(module, n) for n in names]

def filter_subclasses(objects, parent, include_parent=False):
    def is_subclass(obj, parent):
        return isinstance(obj, parent.__class__) and issubclass(obj, parent)

    def filter_func(obj):
        ret = is_subclass(obj, parent)
        if not include_parent:
            ret = ret and obj not in (parent, )
        return ret

    return [obj for obj in objects if filter_func(obj)]

