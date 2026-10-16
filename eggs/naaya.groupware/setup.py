''' naaya.groupware installer '''
from setuptools import setup, find_namespace_packages

setup(name='naaya.groupware',
      version='2.0.2.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['Products.*', 'naaya.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 6.0.1',
          'naaya.content.bfile >= 2.0.0',
          'be.ldapadmin >= 1.0',
      ]
      )
