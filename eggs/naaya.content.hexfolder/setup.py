from setuptools import setup, find_namespace_packages

setup(name='naaya.content.hexfolder',
      version='1.0.0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 5.0.30',
      ]
      )
