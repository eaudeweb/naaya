from setuptools import setup, find_packages

setup(
    name='Products.NaayaForum',
    version='1.2.22',
    description="Naaya Forum",
    long_description=open("README.rst").read() + "\n" +
                open("CHANGELOG.rst").read(),
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    license='MPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Naaya >= 3.4.15',
        'naaya.sql'
        ],
    )
