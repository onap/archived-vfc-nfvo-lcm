#!/bin/bash

#MYSQL_ROOT_PASSWORD=123
PROXY_ARGS=""

if [ $HTTP_PROXY ]; then
    PROXY_ARGS+="--build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    PROXY_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi

function build_lcm {
    cd ../
    docker build ${PROXY_ARGS} -f docker/Dockerfile -t lcm .
}

build_lcm

