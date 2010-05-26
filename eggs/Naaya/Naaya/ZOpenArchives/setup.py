#!/usr/bin/env python
from setuptools import setup

setup(
    name='ZOpenArchives',
    version='1.3',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/Naaya/ZOpenArchives',
    license='GPL',
    packages=['src', ],
    zip_safe = False,
    requires=[
        'lxml',
    ],
)
