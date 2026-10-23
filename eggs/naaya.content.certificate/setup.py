from setuptools import setup, find_namespace_packages

setup(name='naaya.content.certificate',
      version='1.0.3.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 4.2.13',
      ]
      )
