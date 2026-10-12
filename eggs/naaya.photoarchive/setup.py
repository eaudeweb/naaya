from setuptools import setup, find_namespace_packages

setup(name='naaya.photoarchive',
      version='1.5.3',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_namespace_packages(include=['Products.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires='Naaya >= 3.4.0'
      )
