#/bin/bash
#
# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

pip install PyMySQL==0.9.3
mkdir -p /service/vfc/nfvo/lcm/resources/bin/logs
mkdir -p /var/log/onap/vfc/nslcm/

if [ ! -f /service/vfc/nfvo/lcm/resources/bin/logs/django.log ]; then
    touch /service/vfc/nfvo/lcm/resources/bin/logs/django.log
else
    echo >/service/vfc/nfvo/lcm/resources/bin/logs/django.log
fi
if [ ! -f /var/log/onap/vfc/nslcm/runtime_nslcm.log ]; then
    touch /var/log/onap/vfc/nslcm/runtime_nslcm.log
else
    echo >/var/log/onap/vfc/nslcm/runtime_nslcm.log
fi


MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`
MYSQL_USER=`echo $MYSQL_AUTH | cut -d: -f 1`
MYSQL_ROOT_PASSWORD=`echo $MYSQL_AUTH | cut -d: -f 2`

function create_database {
    #cd /service/vfc/nfvo/db/resources/nslcm/bin
    cd /service/vfc/nfvo/lcm/resources/bin
    bash initDB.sh $MYSQL_USER $MYSQL_ROOT_PASSWORD $MYSQL_PORT $MYSQL_IP
    man_path=/service/vfc/nfvo/lcm
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

if [ ! -f /service/vfc/nfvo/lcm/docker/db.txt ]; then
    echo 1 > /service/vfc/nfvo/lcm/docker/db.txt
    echo `pwd` >> db.txt
    create_database
else
    echo "database already existed"
fi
