#!/bin/bash

# We need to get the version from the pyproject.toml file. This grep command searches through for the version
ver=$(cat pyproject.toml | grep -Po '(version\s*=\s*")\K[^"]*')

# Check if the project version is less than or equal to the GitHub tag; if it is then raise an error
if [ $ver <= "$1" ]
then
    echo "Expected version $ver to be greater than current version of $1"
    exit 1
else
    echo "Project version $ver is greater than $1"
fi
