#!/bin/sh

CONFIG_DIR="${BCH_CONFIG_DIR:-/root/bch_rental_engine/config}"
ENV_FILE="${CONFIG_DIR}/.env"
ENV_EXAMPLE_FILE="/app/.env.example"

mkdir -p "${CONFIG_DIR}"

if [ ! -f "${ENV_FILE}" ]; then
  echo "No .env file found at ${ENV_FILE}."

  if [ -f "${ENV_EXAMPLE_FILE}" ]; then
    echo "Creating ${ENV_FILE} from the packaged example configuration."
    cp "${ENV_EXAMPLE_FILE}" "${ENV_FILE}"
  else
    echo "ERROR: Packaged example configuration not found at ${ENV_EXAMPLE_FILE}."
    exit 1
  fi
fi

set -a
. "${ENV_FILE}"
set +a

while true
do
  echo "Running BCH engine $(date)"
  python /app/scripts/bch_solo_rental_strike_engine.py
  sleep 300
done
