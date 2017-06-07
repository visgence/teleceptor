FROM debian:wheezy


# Environment variables
ENV DEBIAN_FRONTEND noninteractive
#Base Debian Install
RUN apt-get update && apt-get -y upgrade && apt-get clean
RUN apt-get -y install --no-install-recommends bash sudo cron vim git python2.7 python-pip sqlite3 ca-certificates  python-sqlite && apt-get clean

#Postgres
RUN apt-get -y install make automake gcc build-essential && apt-get clean
RUN apt-get -y install postgresql && apt-get clean
RUN apt-get -y install python-dev && apt-get clean
RUN apt-get -y install libpq-dev && apt-get clean

#pip dependicies
RUN pip install sqlalchemy cherrypy requests pySerial pyelasticsearch psycopg2 delorean

RUN apt-get -y install vim curl && apt-get clean
#Install teleceptor software as teleceptor user
VOLUME ['/home/tele/teleceptor']
WORKDIR /home/tele/teleceptor

#RUN adduser --disabled-password --gecos "" teleceptor
#USER teleceptor
#WORKDIR /home/teleceptor/
#RUN git clone https://github.com/visgence/teleceptor.git
#RUN mkdir -p /home/teleceptor/.config/teleceptor/
#VOLUME /home/teleceptor/.config/teleceptor/

#WORKDIR /
#USER root



EXPOSE 8000

