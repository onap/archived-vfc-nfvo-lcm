#!/bin/bash

function install_python_libs {
    cd /service/vfc/nfvo/lcm/
    pip install -r requirements.txt
}

function start_redis_server {
    redis-server &
}

function start_mysql {
    su mysql -c /usr/bin/mysqld_safe &
    service mysql start
    # Wait for mysql to initialize; Set mysql root password
    for i in {1..10}; do
        sleep $i
        bash /usr/bin/mysqladmin -u root password $MYSQL_ROOT_PASSWORD &> /dev/null && break
    done
}

function create_database {
    cd /service/vfc/nfvo/lcm/resources/bin
    bash initDB.sh root $MYSQL_ROOT_PASSWORD 3306 127.0.0.1
}

install_python_libs
start_redis_server
start_mysql
create_database
