#!/usr/bin/env sh
pypath=$(which python2.6-config 2> /dev/null)

if [ ! -z $pypath ] 
then
    python ${pypath} $@
else 
    echo 'ERROR: no python2.6-config' 1>&2
    false
fi 
