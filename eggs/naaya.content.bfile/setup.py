from setuptools import setup, find_namespace_packages

setup(name='naaya.content.bfile',
      version='2.0.1.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 3.4.17',
          'ZODB',
          'zope.proxy >= 3.4',
          'plone.i18n',
      ]
      )
