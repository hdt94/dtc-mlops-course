#!/usr/bin/env bash

set -e

python src/deployments.py \
    --name docker \
    --pool-name ${PREFECT_WORK_POOL:-default-docker-process}
