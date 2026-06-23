#!/bin/sh

set -a
. /app/config/.env
set +a

while true
do
  echo "Running BCH engine $(date)"
  python /app/scripts/bch_solo_rental_strike_engine.py
  sleep 300
done
