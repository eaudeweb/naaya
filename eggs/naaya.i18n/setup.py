from setuptools import setup, find_namespace_packages

setup(name='naaya.i18n',
      version='2.0.2.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
        # -*- entry_points -*-
        [zodbupdate]
        renames=naaya.i18n.patches:rename_dict
        """
      )
