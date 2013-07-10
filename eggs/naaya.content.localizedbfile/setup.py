from setuptools import setup, find_packages

setup(name='naaya.content.localizedbfile',
      version='1.0.6',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'naaya.content.bfile >= 1.3.8',
          'Naaya >= 3.3.0',
      ]
)
