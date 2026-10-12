from setuptools import setup, find_namespace_packages

setup(name='naaya.flowplayer',
      version='2.0.1.dev0',
      description="Flowplayer for naaya",
      long_description=open("README.txt").read(),
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='flowplayer naaya',
      author='Alin Voinea',
      author_email='alin.voinea@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='GPL',
      packages=find_namespace_packages(include=['naaya.*']),
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
