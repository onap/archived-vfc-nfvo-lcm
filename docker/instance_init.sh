#!/bin/bash

function install_python_libs {
    cd /service/vfc/nfvo/lcm/
    pip install -r requirements.txt
}

function start_redis_server {
    redis-server &
}

function start_mysql {
    sed -i "s|bind-address.*|# bind-address = 127.0.0.1|" /etc/mysql/my.cnf
    service mysql restart
    sleep 1
}

function create_database {
    cd /service/vfc/nfvo/lcm/resources/bin
    bash initDB.sh root $MYSQL_ROOT_PASSWORD 3306 127.0.0.1
    cd /service
}

install_python_libs
start_redis_server
start_mysql
create_database
