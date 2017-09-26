from setuptools import setup, find_packages

setup(name='naaya.forum-publish',
      version='0.8.5',
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
