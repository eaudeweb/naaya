# Naaya CMS

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
    git push --recurse-submodules=check
    
For a full reference of the git submodules feature, please check: https://git-scm.com/book/en/v2/Git-Tools-Submodules
