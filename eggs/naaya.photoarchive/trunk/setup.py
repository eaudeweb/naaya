from setuptools import setup, find_packages

setup(name='naaya.photoarchive',
      version='1.5.1',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires='Naaya >= 3.0.7'
)
