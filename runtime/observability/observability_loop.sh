#!/data/data/com.termux/files/usr/bin/bash

cd ~/point_vll_reassembled || exit 1

while true
do
    python runtime/observability/runtime_observability_packet.py \
        >> logs/observability/runtime_observability.log 2>&1

    sleep 15
done

