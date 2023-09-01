# Overview

This is a forked repo from https://github.com/SeleniumHQ/docker-selenium.git
It's purpose is to make small changes to address vulnerabilities in the original repo. You will only be able to build this repo on linux, so if you are on Windows, use WSL Ubuntu distro (https://learn.microsoft.com/en-us/windows/wsl/install)

# How to Rebase

To ensure this repo stays as close to the original repo as possible, it is important to rebase often
1. git remote add upstream https://github.com/SeleniumHQ/docker-selenium.git
2. git fetch upstream
3. git rebase upstream/trunk
4. Deal with any merge conflicts
5. git push --force-with-lease

# Building docker images

1. Make sure to clean up any local images
2. NAME=targetrepo/selenium make build
