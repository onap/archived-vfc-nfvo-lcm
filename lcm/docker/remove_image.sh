#!/bin/bash

function remove_lcm_container {
    docker container stop vfc-nfvo-lcm
    docker container rm vfc-nfvo-lcm
}

function remove_lcm_image {
    docker image rm vfc-nfvo-lcm
}

remove_lcm_container
