#!/bin/bash

python -m unittest -v bl.tests
find ./ -type f -name '*.pyc' -delete && echo "removed pyc files"
