from setuptools import setup, find_packages

setup(
    name='Products.NaayaContent.NyPublication',
    version='1.1.9',
    description="NyPublication",
    long_description=open("README.txt").read() + "\n" +
    open("CHANGELOG.rst").read(),
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    license='MPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 3.4.15'
    ],
)
