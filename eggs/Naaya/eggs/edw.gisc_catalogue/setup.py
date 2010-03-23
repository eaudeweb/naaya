from setuptools import setup, find_packages

setup(name='edw.gisc-catalogue',
      version='0.1dev',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['webob', 'rdflib', 'jinja2'],
      entry_points={
          'paste.app_factory': ['main=edw.gisc_catalogue.represent:factory'],
      },
)
