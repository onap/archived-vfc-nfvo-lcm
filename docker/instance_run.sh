#!/bin/bash

cd /service/vfc/nfvo/lcm
chmod +x run.sh
./run.sh

while [ ! -f logs/runtime_lcm.log ]; do
    sleep 1
done
tail -F logs/runtime_lcm.log