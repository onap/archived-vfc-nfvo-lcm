#!/bin/bash

MYSQL_ROOT_PASSWORD="root"
PROXY_ARGS=""
ORG="onap"
VERSION="1.0.0-SNAPSHOT"
PROJECT="vfc"
IMAGE="nslcm"
DOCKER_REPOSITORY="nexus3.onap.org:10003"

if [ $HTTP_PROXY ]; then
    PROXY_ARGS+="--build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    PROXY_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi

function build_lcm {
    docker build ${PROXY_ARGS} -t ${ORG}/${PROJECT}/${IMAGE}:${VERSION} -t ${ORG}/${PROJECT}/${IMAGE}:latest .
}

function push_lcm {
    docker push ${DOCKER_REPOSITORY}/${ORG}/${PROJECT}/${IMAGE}:${VERSION}
    docker push ${DOCKER_REPOSITORY}/${ORG}/${PROJECT}/${IMAGE}:latest
}

build_lcm
push_lcm
docker image list
