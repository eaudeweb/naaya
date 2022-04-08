''' naaya.groupware installer '''
from setuptools import setup, find_packages

setup(name='naaya.groupware',
      version='1.4.68',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 5.0.0',
          'naaya.content.bfile',
          'collective.autopermission == 1.0b2',
      ]
      )
