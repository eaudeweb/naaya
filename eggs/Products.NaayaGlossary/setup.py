from setuptools import setup, find_namespace_packages

setup(
    name='Products.NaayaGlossary',
    version='2.0.2.dev0',
    description="Naaya Glossary",
    long_description=open("README.txt").read() + "\n" +
    open("CHANGELOG.rst").read(),
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='naaya glossary',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    license='MPL',
    packages=find_namespace_packages(include=['Products.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 6.0.1',
        'setuptools',
        'lxml',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
