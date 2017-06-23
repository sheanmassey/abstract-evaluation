#!/bin/bash

python -m unittest -v ae.tests
find ./ -type f -name '*.pyc' -delete && echo "removed pyc files"
