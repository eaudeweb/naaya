PARENT_BUNDLE = 'Groupware'
BUNDLE_NAME_PREFIX = 'PBE-'

def load_bundles():
    import os.path
    from naaya.core.fsbundles import auto_bundle_package
    bundles_dir = os.path.dirname(__file__)
    auto_bundle_package(bundles_dir, BUNDLE_NAME_PREFIX, PARENT_BUNDLE)
