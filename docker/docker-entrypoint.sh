#!/bin/bash

if [ -z "$SERVICE_IP" ]; then
    export SERVICE_IP=`hostname -i`
fi
echo "SERVICE_IP=$SERVICE_IP"

if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    export MYSQL_ROOT_PASSWORD="root"
fi
echo "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD"

if [ -z "$MSB_ADDR" ]; then
    echo "Missing required variable MSB_ADDR: Microservices Service Bus address <ip>:<port>"
    exit 1
fi
echo "MSB_ADDR=$MSB_ADDR"

# Wait for MSB initialization
echo "Wait for MSB initialization"
for i in {1..5}; do
    curl -sS -m 1 $MSB_ADDR > /dev/null && break
    sleep $i
done

# Configure service based on docker environment variables
vfc/nfvo/lcm/docker/instance_config.sh

# microservice-specific one-time initialization
vfc/nfvo/lcm/docker/instance_init.sh

date > init.log

# Start the microservice
vfc/nfvo/lcm/docker/instance_run.sh
