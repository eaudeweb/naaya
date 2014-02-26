from setuptools import setup, find_packages

setup(name='naaya.ew-aoa-library',
      version='1.0.3',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Naaya',
        'naaya-survey',
      ],
)
