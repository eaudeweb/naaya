import os
from naaya.component.external import load_bundles

def load():
    abs_dir = os.path.abspath(os.path.dirname(__file__))
    load_bundles(
            os.path.join(abs_dir, 'bundle.cfg'),
            os.path.join(abs_dir, '../bundles/')
    )
