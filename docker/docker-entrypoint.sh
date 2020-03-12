#!/bin/bash

if [ -z "$SERVICE_IP" ]; then
    export SERVICE_IP=`hostname -i`
fi
echo "SERVICE_IP=$SERVICE_IP"

if [ -z "$MSB_ADDR" ]; then
    echo "Missing required variable MSB_ADDR: Microservices Service Bus address <ip>:<port>"
    exit 1
fi
echo "MSB_ADDR=$MSB_ADDR"

if [ -z "$MYSQL_ADDR" ]; then
    echo "Missing required variable MYSQL_ADDR: <ip>:<port>"
    exit 1
fi
echo "MYSQL_ADDR=$MYSQL_ADDR"

# Wait for MSB initialization
echo "Wait for MSB initialization"
for i in {1..5}; do
    curl -sS -m 1 $MSB_PROTO://$MSB_ADDR/msb -k > /dev/null
    res=$?
    if [ $res -ne 0 ]; then
        break
    fi
    sleep $i
done

# Wait for DB initialization
echo "Wait for DB initialization"
for i in {1..5}; do
    mysql -u$MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD -h`echo $MYSQL_ADDR | cut -d: -f 1` -P`echo $MYSQL_ADDR | cut -d: -f 2` -e "show databases;" > /dev/null && echo "DB initialization completed" && break
    sleep $i && echo "`echo $MYSQL_ADDR | cut -d: -f 1` connection failed"
done

# Configure service based on docker environment variables
vfc/nfvo/lcm/docker/instance_config.sh

# microservice-specific one-time initialization
vfc/nfvo/lcm/docker/instance_init.sh

date > init.log

# Start the microservice
vfc/nfvo/lcm/docker/instance_run.sh
