#!/bin/bash

# Configure config file based on environment variables
python vfc/nfvo/lcm/lcm/pub/config/config.py
cat vfc/nfvo/lcm/lcm/pub/config/config.py

# microservice-specific one-time initialization
vfc/nfvo/lcm/docker/instance_init.sh

date > init.log

# Start the microservice
vfc/nfvo/lcm/docker/instance_run.sh
