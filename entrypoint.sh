#!/bin/bash
#environment variables TELEUID, TELEGID
#Check if host is osx
if echo $TELEOSTYPE | grep -q 'darwin'
then
    adduser teleceptor
else
    groupadd -g $TELEGID teleceptor
    adduser -u $TELEUID -g $TELEGID teleceptor
fi

chown teleceptor:teleceptor /home/teleceptor
echo 'pg:5432:tele:tele:password' > /home/teleceptor/.pgpass
chown teleceptor:teleceptor /home/teleceptor/.pgpass
chmod 600 /home/teleceptor/.pgpass

cp /home/teleceptor/teleceptor/apache/teleceptor.conf /etc/httpd/conf.d/teleceptor.conf

if [ "$1" == "unittest" ]; then
    su teleceptor -c /home/tele/teleceptor/unittest.sh
else
    sudo su
fi
