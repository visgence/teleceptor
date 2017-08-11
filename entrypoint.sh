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
echo 'pg:5432:tele:tele:password' > /home/tele/.pgpass
chown tele:tele /home/tele/.pgpass
chmod 600 /home/tele/.pgpass

if [ "$1" == "unittest" ]; then
    su tele -c /home/tele/teleceptor/unittest.sh
else
    su tele
fi
