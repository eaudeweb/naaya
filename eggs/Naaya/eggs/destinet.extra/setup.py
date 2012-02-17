from setuptools import setup, find_packages

setup(name='destinet.extra',
    version='1.1.6',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 2.12.35', 'Products.NaayaContent.NyPublication >= 1.1.4'
    ]
)
