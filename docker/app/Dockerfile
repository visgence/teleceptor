FROM almalinux:9.5
LABEL description="Visgence Inc <info@visgence.com>"

RUN dnf install -y epel-release
RUN dnf update -y && dnf clean all
RUN dnf install -y make automake gcc gcc-c++ && yum clean all
RUN dnf install -y python3 python3-devel python3-pip && yum clean all
RUN dnf install -y postgresql-devel postgresql && yum clean all
RUN curl -fsSL https://rpm.nodesource.com/setup_18.x | /bin/bash -
RUN dnf install -y nodejs

RUN dnf install -y screen git

RUN adduser --uid 1000 teleceptor

COPY --chown=1000:1000 . /home/teleceptor/teleceptor

USER teleceptor
WORKDIR /home/teleceptor/teleceptor
RUN python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt
RUN npm install --legacy-peer-deps
RUN npm run webpack
ENTRYPOINT ["/home/teleceptor/teleceptor/entrypoint.sh"]
#VOLUME ["/home/teleceptor/teleceptor"]

EXPOSE 8008
