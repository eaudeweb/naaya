from setuptools import setup, find_packages
import os
version = '1.0'

setup(
    name='zmibespin',
    version=version,
    description="Make every textarea in the Zope2 ZMI a bespin editor",
    long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
    classifiers=['Framework :: Zope2'],
    keywords='Python Javascript Bespin',
    author='Alexandru Plugaru',
    author_email='alexandru.plugaru@gmail.com',
    url='http://github.com/humanfromearth/zmibespin',
    license='MPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires="Zope2"
)
