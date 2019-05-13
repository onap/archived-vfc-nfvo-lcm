#!/bin/bash

sudo chown onap:onap -R /service
find  /service -name '*.sh'|xargs chmod a+x

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
    curl -sS -m 1 $MSB_ADDR > /dev/null && break
    sleep $i
done

# Wait for DB initialization
echo "Wait for DB initialization"
for i in {1..5}; do
    curl -sS -m 1 $MYSQL_ADDR > /dev/null && break
    sleep $i
done

# Configure service based on docker environment variables
vfc/nfvo/lcm/docker/instance_config.sh

# microservice-specific one-time initialization
vfc/nfvo/lcm/docker/instance_init.sh

date > init.log

# Start the microservice
vfc/nfvo/lcm/docker/instance_run.sh
