#!/bin/bash

set -e

prefect worker start --pool "${PREFECT_WORK_POOL:-default-docker-process}"
