#!/bin/bash

cd /service/vfc/nfvo/lcm/lcm
./run.sh

while [ ! -f logs/nfvo_lcm.log ]; do
    sleep 1
done
tail -F logs/nfvo_lcm.log