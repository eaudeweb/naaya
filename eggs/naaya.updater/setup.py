from setuptools import setup, find_namespace_packages

setup(name='naaya.updater',
      version='2.0.6.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_namespace_packages(include=['Products.*']),
      include_package_data=True,
      zip_safe=False,
      url='https://github.com/eaudeweb/naaya/tree/master/eggs/naaya.updater/',
      install_requires=[
          'setuptools',
          'Naaya >= 6.0.1',
      ]
      )
