#!/bin/sh

SETUPTOOLS=`grep "setuptools\s*\=\s*" versions.cfg | sed 's/\s*=\s*/==/g'`
ZCBUILDOUT=`grep "zc\.buildout\s*=\s*" versions.cfg | sed 's/\s*=\s*/==/g'`

if [ -s "bin/activate" ]; then
  echo "Updating setuptools: ./bin/easy_install" $SETUPTOOLS
  ./bin/easy_install $SETUPTOOLS

  echo "\n============================================================="
  echo "Buildout is already installed."
  echo "Please remove bin/activate if you want to re-run this script."
  echo "=============================================================\n"

  exit 0
fi

echo "Installing virtualenv"
wget "http://eggrepo.eea.europa.eu/pypi/virtualenv/virtualenv-1.6.4.tar.gz" -O "/tmp/virtualenv-1.6.4.tar.gz"
tar -zxvf "/tmp/virtualenv-1.6.4.tar.gz" -C "/tmp/"

echo "Running: python2.6 virtualenv.py --clear --no-site-packages ."
python2.6 "/tmp/virtualenv-1.6.4/virtualenv.py" --clear  --no-site-packages .
rm "/tmp/virtualenv-1.6.4.tar.gz"
rm -r "/tmp/virtualenv-1.6.4"

echo "Updating setuptools: ./bin/easy_install" $SETUPTOOLS
./bin/easy_install $SETUPTOOLS

echo "Installing zc.buildout: $ ./bin/easy_install" $ZCBUILDOUT
./bin/easy_install $ZCBUILDOUT

echo "\n======================================="
echo "All set. Now you can run ./bin/buildout"
echo "=======================================\n"
