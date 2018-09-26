from setuptools import setup, find_packages

setup(name='naaya.updater',
      version='1.2.32',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      url='https://github.com/eaudeweb/naaya/tree/master/eggs/naaya.updater/',
      install_requires=[
          'setuptools',
          'Naaya',
      ]
      )
