#!/bin/sh

CONFIG_DIR="${BCH_CONFIG_DIR:-/root/bch_rental_engine/config}"

set -a
. "${CONFIG_DIR}/.env"
set +a

while true
do
  echo "Running BCH engine $(date)"
  python /app/scripts/bch_solo_rental_strike_engine.py
  sleep 300
done
