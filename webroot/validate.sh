#!/bin/bash
dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
echo "Setting Path to $dir"
cd $dir
#Exit on non-zero
set -e

#Run npm install
npm install

#Run html validator
./node_modules/.bin/htmlhint --config htmlhint.conf ./templates/

#Run javascript validator
./node_modules/.bin/jshint ./js

#Run css validator
./node_modules/.bin/csslint ./css

#run python validator
pep8 --max-line-length=140 ./*.py
