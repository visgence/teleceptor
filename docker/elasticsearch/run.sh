#!/bin/bash
docker run -tiPd -p 9200:9200 --name tele_es elasticsearch:5.6
docker run -tiPd -p 5601:5601 --link tele_es:elasticsearch --name tele_kibana kibana:5.6
