FROM centos:7
MAINTAINER Visgence Inc <info@visgence.com>

RUN yum install -y epel-release
# bzip2 required by phantomjs
# git required by bower, bower required by bootstrap-treeview.
RUN yum install -y screen vim wget bzip2 git sudo cron sqlite3 ca-certificates python-sqlite postgresql python-devel postgresql-devel curl make automake gcc gcc-c++ && yum clean all

RUN yum install -y python-setuptools && yum clean all
RUN easy_install pip

ADD requirements.txt .
RUN pip install -r requirements.txt

#Install node from package
RUN wget https://nodejs.org/download/release/v6.10.2/node-v6.10.2-linux-x64.tar.gz
RUN tar --strip-components 1 -xzvf node-v* -C /usr/local

# bower needs to be able to be run by root.
RUN npm install -g bower
RUN touch /root/.bowerrc
RUN echo "{ \"allow_root\": true}" >> /root/.bowerrc


VOLUME ["/home/tele"]
WORKDIR /home/tele


EXPOSE 8000
