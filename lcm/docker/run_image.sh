#!/bin/bash

function run_lcm {
    docker run -it --name vfc-nfvo-lcm -p 3306:3306 -p 8403:8403 vfc-nfvo-lcm
}

run_lcm