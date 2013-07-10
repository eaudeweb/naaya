from setuptools import setup, find_packages

setup(name='naaya.content.bfile',
      version='1.3.12',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 3.3.0',
          'ZODB3 >= 3.8',
          'zope.proxy >= 3.4',
      ]
)
