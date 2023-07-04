#!/bin/bash

set -e

POOL="${PREFECT_WORK_POOL:-default-docker-process}"

if [[ -z "$(prefect work-pool ls | grep "${POOL}")" ]]; then
    prefect work-pool create --type process "${POOL}"
elif [[ -z "$(prefect work-pool inspect "${POOL}")" ]]; then
    prefect work-pool create --type process "${POOL}"
else
    echo "Pool already exists: ${POOL}"
fi
