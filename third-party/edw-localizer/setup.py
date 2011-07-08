from setuptools import setup, find_packages

setup(name='edw-localizer',
      version='1.2.3.6', #EDW version .6 based on localizer 1.2.3
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
)
