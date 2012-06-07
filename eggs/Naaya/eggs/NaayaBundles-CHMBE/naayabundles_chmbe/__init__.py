PARENT_BUNDLE = 'CHMBE'
BUNDLE_NAME_PREFIX = 'CHMBE-'

def load_bundles():
    import os.path
    from naaya.core.fsbundles import auto_bundle_package, register_bundle_factory
    bundles_dir = os.path.dirname(__file__)
    auto_bundle_package(bundles_dir, BUNDLE_NAME_PREFIX, PARENT_BUNDLE)
    register_bundle_factory(bundles_dir, BUNDLE_NAME_PREFIX, 'CHM3-BE')
