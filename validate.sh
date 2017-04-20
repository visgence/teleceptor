#!/bin/bash
dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
echo "Setting Path to $dir"
cd $dir
#Exit on non-zero
set -e

#Run html validator
./webroot/node_modules/.bin/htmlhint --config htmlhint.conf ./webroot/templates/

#Run javascript validator
./webroot/node_modules/.bin/jshint ./webroot/js

#Run css validator
./webroot/node_modules/.bin/csslint ./webroot/css

#run python validator
pep8 * --max-line-length=140 ./*.py
