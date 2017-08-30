FROM ubuntu:14.04

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
ARG MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY
ENV MYSQL_ROOT_PASSWORD $MYSQL_ROOT_PASSWORD

RUN apt-get update && \
    apt-get install -y python-dev && \
    apt-get install -y python-pip && \
    apt-get install -y libmysqlclient-dev && \
    apt-get install -y redis-server

ADD . /lcm
RUN cd /lcm; \
    pip install -r requirements.txt

RUN echo "mysql-server mysql-server/root_password password "$MYSQL_ROOT_PASSWORD | debconf-set-selections
RUN echo "mysql-server mysql-server/root_password_again password "$MYSQL_ROOT_PASSWORD | debconf-set-selections
RUN apt-get install -y mysql-server && apt-get install -y mysql-client

EXPOSE 8403
EXPOSE 3306

WORKDIR /

CMD lcm/docker/init_script.sh
