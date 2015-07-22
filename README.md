# Naaya CMS

## Working with git submodules

This repository contains links to other git repositories, as described in `.gitmodules`.

To update code to latest version, use:

    git submodule update --remote
    
To push changes commited inside submodule folders, use:

    git push --recurse-submodules=check
    
For a full reference of the git submodules feature, please check: https://git-scm.com/book/en/v2/Git-Tools-Submodules
