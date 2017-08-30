FROM ubuntu:14.04

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
#ARG MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY

RUN apt-get update && \
    apt-get install -y python-dev && \
    apt-get install -y python-pip && \
    apt-get install -y libmysqlclient-dev

ADD . /lcm
RUN cd /lcm; \
    pip install -r requirements.txt

RUN echo "mysql-server mysql-server/root_password password root" | debconf-set-selections
RUN echo "mysql-server mysql-server/root_password_again password root" | debconf-set-selections
RUN apt-get install -y mysql-server && apt-get install -y mysql-client

EXPOSE 8403
EXPOSE 3306

WORKDIR /

RUN { \
                echo '#!/bin/bash'; \
                echo 'service mysql start'; \
                echo 'mysql -uroot -proot < lcm/resources/dbscripts/mysql/vfc-nfvo-lcm-createdb.sql'; \
                echo 'mysql -uroot -proot < lcm/resources/dbscripts/mysql/vfc-nfvo-lcm-createobj.sql'; \
                echo 'python lcm/manage.py migrate'; \
                echo 'python lcm/manage.py runserver 127.0.0.1:8403'; \
    } > init_script.sh && chmod +x init_script.sh

CMD ./init_script.sh
