#!/bin/bash
######
# by vfc-db test
#####
# echo "No service needs init."
#MYSQL_USER=$1
######

pip install PyMySQL==0.9.3
mkdir -p /service/logs
mkdir -p /service/vfc/nfvo/lcm/docker/nslcm/bin/logs/
mkdir -p /var/log/onap/vfc/nslcm/
if [ ! -f /service/logs/django.log ]; then
    touch /service/logs/django.log
else
    echo >/service/logs/django.log
fi
if [ ! -f /service/vfc/nfvo/lcm/docker/nslcm/bin/logs/django.log ]; then
    touch /service/vfc/nfvo/lcm/docker/nslcm/bin/logs/django.log
else
    echo >/service/vfc/nfvo/lcm/docker/nslcm/bin/logs/django.log
fi
if [ ! -f /var/log/onap/vfc/nslcm/runtime_nslcm.log ]; then
    touch /var/log/onap/vfc/nslcm/runtime_nslcm.log
else
    echo >/var/log/onap/vfc/nslcm/runtime_nslcm.log
fi
######
MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`
MYSQL_USER=`echo $MYSQL_AUTH | cut -d: -f 1`
MYSQL_ROOT_PASSWORD=`echo $MYSQL_AUTH | cut -d: -f 2`

function create_database {
    #cd /service/vfc/nfvo/db/resources/nslcm/bin
    cd /service/vfc/nfvo/lcm/docker/nslcm/bin
    bash initDB.sh $MYSQL_USER $MYSQL_ROOT_PASSWORD $MYSQL_PORT $MYSQL_IP
    #DIRNAME=`dirname $0`
    #HOME=`cd $DIRNAME/; pwd`
    #man_path=$HOME/../
    man_path=/service/vfc/nfvo/lcm
    #tab=`mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -P${MYSQL_PORT} -h${MYSQL_IP} -e "use vfcnfvolcm; select count(*) from vfcnfvolcm;"`
    tab=`mysql -u${MYSQL_USER} -p${MYSQL_ROOT_PASSWORD} -P${MYSQL_PORT} -h${MYSQL_IP} -e "SELECT count(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA='vfcnfvolcm';"`
    tab1=`echo $tab |awk '{print $2}'`
	echo "=========="
	echo $tab1
	echo "=========="
    if [ $tab1 -eq 0 ] ; then
	echo "============"
	echo $tab1
	echo "============"
        echo "TABLE NOT EXISTS, START MIGRATE"
        python $man_path/manage.py makemigrations && python $man_path/manage.py migrate &
        wait
        tab2=`mysql -u${MYSQL_USER} -p${MYSQL_ROOT_PASSWORD} -P${MYSQL_PORT} -h${MYSQL_IP} -e "SELECT count(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA='vfcnfvolcm';"`
	tab3=`echo $tab2|awk '{print $2}'`
        if [ $tab3 -gt 0  ] ; then
        echo "TABLE CREATE uUCCESSFUL"
    fi
else
    echo "table already existed"
    exit 1
fi
 }

if [ ! -f db.txt ]; then
    echo 1 > db.txt
    echo `pwd` >> db.txt
    create_database
else
    echo "database already existed"
fi
