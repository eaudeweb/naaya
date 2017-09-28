from setuptools import setup, find_packages

setup(name='eea.gisc-gnaccess',
    version='0.1dev',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['repoze.configuration', 'jpype'],
    entry_points="""\
        [console_scripts]
        gnaccess = eea.gisc_gnaccess.command:main

        [repoze.configuration.directive]
        gisc_gnaccess_javadb = eea.gisc_gnaccess.javadb:config_directive
        gisc_gnaccess_output = eea.gisc_gnaccess.command:config_directive
    """,
)
