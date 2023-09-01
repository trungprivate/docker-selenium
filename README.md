# Overview

This is a forked repo from https://github.com/SeleniumHQ/docker-selenium.git
It's purpose is to make small changes to address vulnerabilities in the original repo

# How to Rebase

To ensure this repo stays as close to the original repo as possible, it is important to rebase often
1. git remote add upstream https://github.com/SeleniumHQ/docker-selenium.git
2. git fetch upstream
3. git rebase upstream/trunk
4. Deal with any merge conflicts
5. git push --force-with-lease

# Building docker images

1. Make sure to clean up any local images
2. NAME=selenium make build
