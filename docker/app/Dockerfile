FROM almalinux:9.5
LABEL description="Visgence Inc <info@visgence.com>"

RUN dnf install -y epel-release
RUN dnf update -y && dnf clean all
RUN dnf install -y make automake gcc gcc-c++ && yum clean all
RUN dnf install -y python3.12 python3.12-devel python3.12-pip && yum clean all
RUN dnf install -y postgresql-devel postgresql && yum clean all
RUN curl -fsSL https://rpm.nodesource.com/setup_18.x | /bin/bash -
RUN dnf install -y nodejs

RUN dnf install -y screen git

RUN adduser --uid 1000 teleceptor


USER teleceptor
WORKDIR /home/teleceptor/teleceptor
#Copy requirements.txt first to leverage docker cache
COPY --chown=1000:1000 requirements.txt /home/teleceptor/teleceptor/requirements.txt
RUN python3.12 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt

# Copy node_modules and package.json to leverage docker cache
COPY --chown=1000:1000 package.json /home/teleceptor/teleceptor/package.json
COPY --chown=1000:1000 package-lock.json /home/teleceptor/teleceptor/package-lock.json
RUN npm install --legacy-peer-deps

#Copy the rest of the code
COPY --chown=1000:1000 . /home/teleceptor/teleceptor

#Build the frontend
RUN npm run webpack


ENTRYPOINT ["/home/teleceptor/teleceptor/entrypoint.sh"]
#VOLUME ["/home/teleceptor/teleceptor"]

EXPOSE 8008
