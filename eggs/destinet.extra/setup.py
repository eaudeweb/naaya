''' destinet.extra installer '''
from setuptools import setup, find_packages

setup(name='destinet.extra',
      version='2.0.3.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 6.0.1',
          'naaya.content.bfile >= 2.0.0',
          'Products.NaayaContent.NyPublication >= 2.0.0',
          'naaya.envirowindows >= 2.0.1',
          'naayabundles-destinet',
      ]
      )
