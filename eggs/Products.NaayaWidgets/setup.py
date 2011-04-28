from setuptools import setup, find_packages

setup(
    name='Products.NaayaWidgets',
    version="1.2.2",
    author='EaudeWeb',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro/',
    license='MPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Naaya'],
)
