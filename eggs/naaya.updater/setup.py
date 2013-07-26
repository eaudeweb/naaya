from setuptools import setup, find_packages

setup(name='naaya.updater',
    version='1.2.31',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/naaya.updater/',
    install_requires=[
        'setuptools',
        'Naaya',
    ]
)
