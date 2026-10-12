from setuptools import setup, find_namespace_packages

setup(name='naaya.content.goodpracticebusiness',
      version='1.0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'naaya.content.bfile',
          'Naaya >= 3.3.0',
      ]
      )
