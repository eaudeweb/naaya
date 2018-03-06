from setuptools import setup, find_packages

setup(name='naaya.content.certificate',
      version='0.0.1',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 4.2.13',
      ]
      )
