#!/bin/bash

function run_lcm {
    docker run --name lcm -d -p 3306:3306 -p 8403:8403 --env-file env.list lcm
}

run_lcm
