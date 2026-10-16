from setuptools import setup, find_packages

setup(name='naaya.forum-publish',
      version='2.0.0.dev0',
      description="Publish for Forum",
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      license='MPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Products.NaayaForum',
          'scrubber'
      ],
)
