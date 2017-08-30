#!/bin/bash

function run_lcm {
    docker run -it -p 3306:3306 -p 8403:8403 lcm
}

run_lcm
