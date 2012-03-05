from setuptools import setup, find_packages

setup(name='naaya.flowplayer',
      version='1.1.7',
      description="Flowplayer for naaya",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGELOG.rst").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='flowplayer naaya',
      author='Alin Voinea',
      author_email='alin.voinea@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['naaya'],
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
