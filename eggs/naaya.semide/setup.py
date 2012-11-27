from setuptools import setup, find_packages

setup(name='naaya.semide',
    version='1.1.7',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 3.2.4',
        'Products.NaayaCalendar',
        'Products.NaayaForum',
        'Products.NaayaGlossary',
        'Products.NaayaLinkChecker',
        'Products.NaayaThesaurus',
        'Products.NaayaProfilesTool',
        'naaya.photoarchive',
        'edw-ZOpenArchives',
        'edw-reportlab',
        'pyfribidi',
        'python-memcached',
    ]
)
