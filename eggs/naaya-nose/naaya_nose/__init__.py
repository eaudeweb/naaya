import sys
import os
import re
import ast
from os import path
from time import time
import logging

log = logging.getLogger('naaya nose')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stderr))


def patch_sys_path(buildout_part_name):
    """Extract sys.path entries from the buildout instance script and add
    them to the current process's sys.path.  Also apply the monkey-patches
    defined in the script (namespace package fixes, broken __provides__).
    """
    buildout_root = path.dirname(path.dirname(os.path.abspath(sys.argv[0])))
    part_script = path.join(buildout_root, 'bin', buildout_part_name)

    if not path.isfile(part_script):
        part_script += '-script.py'
        if not path.isfile(part_script):
            raise RuntimeError("Cannot find instance script: %s" % part_script)

    with open(part_script, 'r') as f:
        script_text = f.read()

    # Extract the sys.path list from the script.
    # The script contains: sys.path[0:0] = [ ... ]
    m = re.search(r'sys\.path\[0:0\]\s*=\s*\[([^\]]+)\]', script_text, re.DOTALL)
    if m:
        paths_text = '[' + m.group(1) + ']'
        paths = ast.literal_eval(paths_text)
        sys.path[0:0] = paths
    else:
        raise RuntimeError("Cannot find sys.path setup in %s" % part_script)

    # Apply the namespace package fix and the __provides__ monkey-patches
    # that are defined in the generated instance script.
    _fix_ns_paths_code = """
import sys, os
def _fix_ns_paths(packageName):
    mod = sys.modules.get(packageName)
    if mod is None:
        return
    ns_path = packageName.replace('.', os.sep)
    current = set(getattr(mod, '__path__', []))
    for sp in sys.path:
        candidate = os.path.join(sp, ns_path)
        if os.path.isdir(candidate) and candidate not in current:
            mod.__path__.append(candidate)
            current.add(candidate)
try:
    import pkg_resources
    for ns_name in list(pkg_resources._namespace_packages.keys()):
        _fix_ns_paths(ns_name)
    _orig_declare_ns = pkg_resources.declare_namespace
    def _patched_declare_namespace(packageName):
        _orig_declare_ns(packageName)
        _fix_ns_paths(packageName)
    pkg_resources.declare_namespace = _patched_declare_namespace
except Exception:
    pass
try:
    import zope.interface.declarations as _zid
    _orig_normalizeargs = _zid._normalizeargs
    def _safe_normalizeargs(sequence, output=None):
        if output is None:
            output = []
        cls = sequence.__class__
        if _zid.InterfaceClass in cls.__mro__ or _zid.Implements in cls.__mro__:
            output.append(sequence)
        else:
            try:
                for v in sequence:
                    _safe_normalizeargs(v, output)
            except TypeError:
                pass
        return output
    _zid._normalizeargs = _safe_normalizeargs
except Exception:
    pass
"""
    exec(compile(_fix_ns_paths_code, '<naaya-nose-patches>', 'exec'),
         {'__builtins__': __builtins__})


def call_testrunner(tzope, buildout_root):
    """Run tests with zope.testrunner."""
    from Products.Naaya.tests.NaayaTestCase import NaayaTestLayer
    NaayaTestLayer.initialize(tzope)

    # Collect test paths from src/ symlinks directory, but only for eggs
    # that are on the current instance's sys.path.
    src_dir = path.join(buildout_root, 'src')
    real_sys_paths = set(path.realpath(p) for p in sys.path)
    defaults = []
    if path.isdir(src_dir):
        for name in sorted(os.listdir(src_dir)):
            egg_dir = path.realpath(path.join(src_dir, name))
            if path.isdir(egg_dir) and egg_dir in real_sys_paths:
                defaults.extend(['--test-path', egg_dir])

    from zope.testrunner import run
    run(defaults=defaults)


def main(buildout_part_name=None):
    """
    Main entry point. Set up Zope 5 and then call ``zope.testrunner``.

    Takes a single argument, ``buildout_part_name`` (e.g. "destinet").
    It can be provided as a function argument or as a command-line argument.
    """
    if buildout_part_name is None:
        buildout_part_name = sys.argv[1]
    # Always remove the buildout part name from argv so it doesn't leak
    # into zope.testrunner as a legacy module filter.
    if len(sys.argv) > 1 and sys.argv[1] == buildout_part_name:
        del sys.argv[1]

    log.info("Preparing Zope environment ...")
    t0 = time()
    patch_sys_path(buildout_part_name)
    buildout_root = path.dirname(path.dirname(os.path.abspath(sys.argv[0])))
    from naaya_nose.zope_wrapper import zope_test_environment
    tzope = zope_test_environment(buildout_part_name)
    log.info("Zope environment loaded in %.3f seconds" % (time() - t0))
    log.info("Calling zope.testrunner ... ")
    call_testrunner(tzope, buildout_root)
