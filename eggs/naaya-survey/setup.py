from setuptools import setup, find_namespace_packages

setup(
    name='naaya-survey',
    version="2.0.1.dev0",
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro/',
    license='MPL',
    packages=find_namespace_packages(include=['Products.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Naaya',
                      'xlsxwriter',
                      'pdfkit',
                      'naaya.i18n >= 1.1.8'],
)
