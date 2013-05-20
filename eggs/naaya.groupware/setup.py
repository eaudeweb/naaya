from setuptools import setup, find_packages

setup(name='naaya.groupware',
      version='1.3.10',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 3.2.34',
          'naaya.content.bfile',
          'eea.usersdb >= 1.2.0'
      ]
)
