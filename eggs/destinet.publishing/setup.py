from setuptools import setup, find_packages

setup(name='destinet.publishing',
    version='1.0',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 2.12', 'Products.NaayaContent.NyPublication'
    ]
)
