#!/bin/sh

# Pytest
echo "Running pre-commit hook"
pytest -vv -p no:cacheprovider

if [ $? -ne 0 ]; then
 echo "Tests must pass before committing"
 exit 1
fi
####

# Prevent master commit
branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$branch" = "master" ]; then
  echo "You can't commit directly to master branch"
  exit 1
fi
####