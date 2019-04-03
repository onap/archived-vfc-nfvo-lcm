#!/bin/bash
#
# Copyright 2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

DIRNAME=`dirname $0`
HOME=`cd $DIRNAME/; pwd`
MYSQL_USER=$1
MYSQL_PASSWORD=$2
MYSQL_PORT=$3
MYSQL_IP=$4
echo "start create vfcnfvolcm db"
sql_path=$HOME/../
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -P$MYSQL_PORT -h$MYSQL_IP <$sql_path/dbscripts/mysql/vfc-nfvo-lcm-createdb.sql
sql_result=$?
if [ $sql_result -ne 0 ] ; then
    echo "Failed to create vfcnfvolcm database"
    exit 1
else
    echo "Create vfcnfvolcm database successfully"
    exit 0
fi

