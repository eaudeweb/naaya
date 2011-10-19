from setuptools import setup, find_packages

setup(name='naaya.chm',
    version='2.4.9',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 2.12',
        'naaya.photoarchive',
        'Products.NaayaLinkChecker',
        'Products.NaayaNetRepository',
        'Products.NaayaHelpDeskAgent',
        'Products.NaayaGlossary',
        'Products.NaayaCalendar',
        'Products.NaayaForum'
    ]
)
