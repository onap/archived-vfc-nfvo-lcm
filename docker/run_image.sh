#!/bin/bash

function run_lcm {
    docker run -it --name vfc-nslcm -p 3306:3306 -p 8403:8403 onap/vfc/nslcm
}

run_lcm