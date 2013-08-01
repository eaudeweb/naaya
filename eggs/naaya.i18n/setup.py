from setuptools import setup, find_packages

setup(name='naaya.i18n',
      version='1.1.8',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
        # -*- entry_points -*-
        [zodbupdate]
        renames=naaya.i18n.patches:rename_dict
        """
)
