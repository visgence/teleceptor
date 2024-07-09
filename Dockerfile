FROM ubuntu:24.04
LABEL Visgence Inc <info@visgence.com>

RUN apt-get update && apt-get install -y screen vim sudo cron sqlite3 ca-certificates nginx net-tools
RUN apt-get install -y postgresql python3-dev make automake gcc build-essential python3-pip
RUN apt-get install -y libapache2-mod-wsgi-py3 curl apache2 wget

RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install nodejs -y

ADD requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

RUN userdel -r ubuntu
RUN useradd --uid 1000 --home /home/teleceptor --shell /bin/bash teleceptor

VOLUME ["/home/teleceptor"]
WORKDIR /home/teleceptor/teleceptor

COPY . .

RUN cp ./scripts/nginx.conf /etc/nginx/sites-available/default
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
RUN cp ./scripts/gunicorn.* /etc/systemd/system/

EXPOSE 8000

ENTRYPOINT [ "sh", "/home/teleceptor/teleceptor/entrypoint.sh" ]
