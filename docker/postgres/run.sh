#!/bin/bash
docker run -t -i -P -d \
    --name tele_postgres \
    -e POSTGRES_DB=tele \
    -e POSTGRES_USER=tele \
    -e POSTGRES_PASSWORD=password \
    postgres:9.2

