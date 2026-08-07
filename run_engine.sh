#!/bin/sh

CONFIG_DIR="${BCH_CONFIG_DIR:-/config}"
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

RUN_NOW_TRIGGER="${CONFIG_DIR}/run_now.trigger"
SCHEDULE_SECONDS=300
POLL_SECONDS=5

while true
do
  echo "Running BCH engine $(date)"
  python -m scripts.bch_solo_rental_strike_engine

  elapsed=0

  while [ "${elapsed}" -lt "${SCHEDULE_SECONDS}" ]
  do
    if [ -f "${RUN_NOW_TRIGGER}" ]; then
      echo "Immediate engine run requested."
      rm -f "${RUN_NOW_TRIGGER}"
      break
    fi

    sleep "${POLL_SECONDS}"
    elapsed=$((elapsed + POLL_SECONDS))
  done
done
