#!/bin/bash
#environment variables NETREGUID, NETREGGID
#Check if host is osx
if echo $TELEOSTYPE | grep -q 'darwin'
then
    adduser tele
else
    groupadd -g $TELEGID telegroup
    adduser --uid $TELEUID --quiet --gecos "" --disabled-password --gid $TELEGID tele
fi

chown tele /home/tele

if [ "$1" == "unittest" ]; then
    su tele -c /home/tele/teleceptor/unittest.sh
else
    su tele
fi

