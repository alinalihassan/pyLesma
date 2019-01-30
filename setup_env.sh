#!/usr/bin/env bash

# Setup Git Hooks
cd .git/hooks/
ln -s -f ../../.hooks/pre-commit.sh ./pre-commit
