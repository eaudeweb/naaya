from setuptools import setup, find_namespace_packages

setup(name='naaya.photoarchive',
      version='2.0.3.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_namespace_packages(include=['Products.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires='Naaya >= 6.0.1'
      )
