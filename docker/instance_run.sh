#!/bin/bash

cd /service/vfc/nfvo/lcm
chmod +x run.sh
./run.sh

while [ ! -f logs/nfvo_lcm.log ]; do
    sleep 1
done
tail -F logs/nfvo_lcm.log