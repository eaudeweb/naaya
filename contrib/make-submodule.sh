#!/bin/bash

NAME=$1
REPO_PATH=/Users/alex/Projects/bun3/

echo "Please ensure http://github.com/eaudeweb/naaya.$NAME.git exists, prior to running this script"

git svn clone https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/$NAME -A authors-transform.txt 
cd $NAME
git remote add origin git@github.com:eaudeweb/naaya.$NAME.git 
git push -u origin master

cd $REPO_PATH/eggs
git rm -r $NAME
git submodule add git@github.com:eaudeweb/naaya.$NAME.git $NAME
git config -f ../.gitmodules submodule.eggs/$NAME.branch master

git commit -am "Added submodule: $NAME"

echo "Done
