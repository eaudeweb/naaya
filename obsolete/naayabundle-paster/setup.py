from setuptools import setup

version = '0.1'

setup(
    name='naayabundle-paster',
    version=version,
    description="paster templates",
    long_description="""\
naaya bundle paste script""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='paste paster',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro/',
    license='MPL',
    py_modules=['templates'],
    include_package_data=True,
    zip_safe=False,
    packages=[],
    install_requires=[
        'PasteScript',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [paste.paster_create_template]
    naayabundle=templates:NaayaBundleTemplate
    """,
)
