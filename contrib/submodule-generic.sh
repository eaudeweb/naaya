#!/bin/bash

NAME=$1
GIT_REPO=$1.git
REPO_FOLDER=eggs
SVN_FOLDER=trunk/eggs
REPO_PATH=/Users/alex/Projects/bun3/

echo "Please ensure http://github.com/eaudeweb/$GIT_REPO exists, prior to running this script"

echo "Source clone..."
git svn clone https://svn.eionet.europa.eu/repositories/Naaya/$SVN_FOLDER/$NAME -A authors-transform.txt 
cd $NAME
git remote add origin git@github.com:eaudeweb/$GIT_REPO 
git push -u origin master

echo "Submodule..."
cd $REPO_PATH/$REPO_FOLDER
git rm -r $NAME
git submodule add git@github.com:eaudeweb/$GIT_REPO $NAME
git config -f ../.gitmodules submodule.$REPO_FOLDER/$NAME.branch master

git commit -am "Added submodule: $NAME"

echo "Done"
