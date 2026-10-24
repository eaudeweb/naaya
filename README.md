# Naaya CMS

[![tests python 3.12](https://github.com/eaudeweb/naaya/actions/workflows/tests.yml/badge.svg?branch=python3)](https://github.com/eaudeweb/naaya/actions/workflows/tests.yml?query=branch%3Apython3)
[![tests python 3.14](https://github.com/eaudeweb/naaya/actions/workflows/tests-python314.yml/badge.svg?branch=python3)](https://github.com/eaudeweb/naaya/actions/workflows/tests-python314.yml?query=branch%3Apython3)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Python 3.14](https://img.shields.io/badge/python-3.14-blue)
![Zope 6.2](https://img.shields.io/badge/zope-6.2-blue)

## Working with git submodules

This repository contains links to other git repositories, as described in `.gitmodules`.

To clone the entire repository plus linked submodules, use:

    git clone --recursive git@github.com:eaudeweb/naaya.git
    
To update code to latest version, use:

    git submodule update --remote --merge/--rebase
    
To push changes commited inside submodule folders, use:

    # inside submodule folder
    git push
    
    # inside main folder
    git push --recurse-submodules=on-demand
    
For a full reference of the git submodules feature, please check: https://git-scm.com/book/en/v2/Git-Tools-Submodules
