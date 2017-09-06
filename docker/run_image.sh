#!/bin/bash

function run_lcm {
    docker run -it --name vfc-nslcm -p 3306:3306 -p 8403:8403 -e MSB_ADDR=127.0.0.1:80 onap/vfc/nslcm
}

run_lcm