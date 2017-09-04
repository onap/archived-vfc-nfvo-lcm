#!/bin/bash

BUILD_ARGS="--no-cache"
ORG="onap"
VERSION="1.0.0-SNAPSHOT"
PROJECT="vfc"
IMAGE="nslcm"
DOCKER_REPOSITORY="nexus3.onap.org:10003"
IMAGE_NAME="${DOCKER_REPOSITORY}/${ORG}/${PROJECT}/${IMAGE}"

if [ $HTTP_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi

function build_lcm {
    docker build ${BUILD_ARGS} -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .
}

function push_lcm {
    docker push ${IMAGE_NAME}:${VERSION}
    docker push ${IMAGE_NAME}:latest
}

build_lcm
push_lcm
