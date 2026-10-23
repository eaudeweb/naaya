from setuptools import setup, find_namespace_packages

setup(
    name='Products.NaayaContent.NyPublication',
    version='2.0.4.dev0',
    description="NyPublication",
    long_description=open("README.txt").read() + "\n" +
    open("CHANGELOG.rst").read(),
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    license='MPL',
    packages=find_namespace_packages(include=['Products.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya >= 3.4.15'
    ],
)
