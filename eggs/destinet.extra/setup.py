from setuptools import setup, find_packages

setup(name='destinet.extra',
    version='1.2.13',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 3.3.24', 'Products.NaayaContent.NyPublication >= 1.1.4',
        'naaya.envirowindows', 'naayabundles-destinet'
    ]
)
