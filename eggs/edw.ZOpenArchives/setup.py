#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='edw.ZOpenArchives',
    version='1.3',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/',
    license='GPL',
    packages=find_packages(),
    zip_safe=False,
    requires=[
        'lxml',
    ],
    install_requires=[
        'Naaya',
    ],
)
