#!/bin/bash

function remove_lcm_container {
    docker container stop vfc-nslcm
    docker container rm vfc-nslcm
}

function remove_lcm_image {
    docker image rm vfc-nslcm
}

remove_lcm_container
