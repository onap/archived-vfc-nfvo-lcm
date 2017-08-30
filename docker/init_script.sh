#!/bin/bash

function start_mysql {
    service mysql start
    mysql -uroot -p$MYSQL_ROOT_PASSWORD < lcm/resources/dbscripts/mysql/vfc-nfvo-lcm-createdb.sql
    mysql -uroot -p$MYSQL_ROOT_PASSWORD < lcm/resources/dbscripts/mysql/vfc-nfvo-lcm-createobj.sql
}

function edit_configs {
    if [ $MSB_SERVICE_IP ]; then
        sed -i "s|MSB_SERVICE_IP.*|MSB_SERVICE_IP = '$MSB_SERVICE_IP'|" lcm/lcm/pub/config/config.py
    fi

    if [ $REDIS_HOST ]; then
        sed -i "s|REDIS_HOST.*|REDIS_HOST = '$REDIS_HOST'|" lcm/lcm/pub/config/config.py
    fi

    if [ $DB_IP ]; then
        sed -i "s|DB_IP.*|DB_IP = '$DB_IP'|" lcm/lcm/pub/config/config.py
    fi

    if [ $SDC_BASE_URL ]; then
        sed -i "s|SDC_BASE_URL.*|SDC_BASE_URL = '$SDC_BASE_URL'|" lcm/lcm/pub/config/config.py
    fi
}

function start_server {
    cd /lcm/
    python manage.py runserver $sip:8403
    #bash run.sh
}

if [ $MYSQL_ROOT_PASSWORD ]; then
    start_mysql
    edit_configs
    start_server
else
    echo "MYSQL_ROOT_PASSWORD environment variable not set."
fi
