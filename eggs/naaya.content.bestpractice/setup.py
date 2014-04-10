from setuptools import setup, find_packages

setup(name='naaya.content.bestpractice',
      version='0.0.4',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'naaya.content.bfile',
          'Naaya >= 3.3.0',
      ]
)
