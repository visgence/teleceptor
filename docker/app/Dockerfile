FROM centos:7
LABEL Visgence Inc <info@visgence.com>

RUN yum install -y epel-release

RUN yum install -y screen vim sudo cron sqlite3 ca-certificates python-sqlite  && yum clean all
RUN yum install -y postgresql python-devel postgresql-devel make automake gcc gcc-c++ && yum clean all
RUN yum install -y mod_wsgi curl httpd wget python-setuptools && yum clean all

RUN curl -o get-pip.py https://bootstrap.pypa.io/pip/2.7/get-pip.py
RUN python get-pip.py

ADD requirements.txt .
RUN pip install -r requirements.txt

#Install node from package
RUN curl --silent --location https://rpm.nodesource.com/setup_8.x | bash -
RUN yum install -y nodejs-8.6.0-1nodesource

VOLUME ["/home/teleceptor"]
WORKDIR /home/teleceptor

EXPOSE 8000
