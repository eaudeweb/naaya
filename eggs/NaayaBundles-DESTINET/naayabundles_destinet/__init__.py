PARENT_BUNDLE = 'EW'
BUNDLE_NAME_PREFIX = 'DESTINET-'

def load_bundles():
    import os.path
    from naaya.core.fsbundles import auto_bundle_package
    bundles_dir = os.path.dirname(__file__)
    auto_bundle_package(bundles_dir, BUNDLE_NAME_PREFIX, PARENT_BUNDLE)
