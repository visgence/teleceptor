#!/bin/bash
docker run -ti \
            -p 8000:8000 \
            --link tele_es:elasticsearch \
            -v ~/Documents/teleceptor:/home/teleceptor/teleceptor \
            teleceptor \
            /bin/bash
