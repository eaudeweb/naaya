#!/bin/bash

PYTHON_PREFIX=`pwd`/python
mkdir src
mkdir -p ../common/eggs
svn co https://svn.eionet.europa.eu/repositories/Naaya/buildout/groupware/zope212/ src/buildout
svn co https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/NaayaBundles-Groupware/ src/NaayaBundles-Groupware
sed -i 's/naayabundles_forum/naayabundles_groupware/g' src/buildout/naaya.cfg
sed -i 's/NaayaBundles-Forum/NaayaBundles-Groupware/g' src/buildout/buildout.cfg
ln -s src/buildout/buildout.cfg
ln -s src/buildout/versions.cfg
ln -s src/buildout/zope-2.12.26-versions.cfg
ln -s src/buildout/naaya.cfg
ln -s src/buildout/bootstrap.py
ln -s src/buildout/sources.cfg
cp src/buildout/secret.cfg.sample secret.cfg

wget http://eggshop.eaudeweb.ro/Python-2.6.8-edw.tgz
tar zxf Python-2.6.8-edw.tgz
cd Python-2.6.8-edw
./configure --enable-unicode=ucs4 --prefix=$PYTHON_PREFIX
make
make install
cd ..
PYTHON=`pwd`/python/bin/python
rm -rf Python-2.6.8*
$PYTHON bootstrap.py -v1.4.4
./bin/buildout
