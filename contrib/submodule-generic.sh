#!/bin/bash

NAME=$1
GIT_REPO=naaya.buildout.$1.git
REPO_FOLDER=buildout
SVN_FOLDER=buildout
REPO_PATH=/Users/alex/Projects/bun3/

echo "Please ensure http://github.com/eaudeweb/$GIT_REPO exists, prior to running this script"

git svn clone https://svn.eionet.europa.eu/repositories/Naaya/$SVN_FOLDER/$NAME -A authors-transform.txt 
cd $NAME
git remote add origin git@github.com:eaudeweb/$GIT_REPO 
git push -u origin master

cd $REPO_PATH/$REPO_FOLDER
git rm -r $NAME
git submodule add $GIT_REPO $NAME
git config -f ../.gitmodules submodule.$REPO_FOLDER/$NAME.branch master

git commit -am "Added submodule: $NAME"

echo "Done"
