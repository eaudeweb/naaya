from setuptools import setup, find_packages

setup(name='Products.CHM2BE',
      version='1.1.3',
      description="CHM2BE",
      long_description="CHM2BE",
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Eau De Web',
      author_email='office@eaudeweb.ro',
      url=('https://svn.eionet.europa.eu/'
           'repositories/Naaya/trunk/Naaya/Products.CHM2BE'),
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
