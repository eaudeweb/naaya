from setuptools import setup, find_packages

setup(name='naaya.envirowindows',
    version='1.1',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya',
        'Products.LDAPUserFolder',
        'naaya.ew-aoa-library',
        'naaya.content-sdo',
        'naaya.content.talkback',
        'Products.NaayaSurvey',
        'Products.NaayaSimpleSurvey',
        'Products.NyConsultation',
        'Products.RDFCalendar',
        'Products.RDFSummary',
    ]
)
