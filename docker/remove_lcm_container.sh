#!/bin/bash

function remove_lcm_container {
    docker container stop lcm
    docker container rm lcm
}

function remove_lcm_image {
    docker image rm lcm
}

remove_lcm_container
