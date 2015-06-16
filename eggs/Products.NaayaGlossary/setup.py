from setuptools import setup, find_packages

setup(name='Products.NaayaGlossary',
      version='1.1.14',
      description="Naaya Glossary",
      long_description=open("README.txt").read() + "\n" +
      open("CHANGELOG.rst").read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='naaya glossary',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'lxml',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
