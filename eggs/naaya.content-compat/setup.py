from setuptools import setup, find_namespace_packages

setup(name='naaya.content-compat',
      version='2.0.3.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['Products.*']),
      include_package_data=True,
      zip_safe=False,
      )
