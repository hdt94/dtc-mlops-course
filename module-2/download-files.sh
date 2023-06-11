#!/bin/bash

set -e

if [[ -z "${SCRIPTS_DIR}" ]]; then
    echo >&2 "missing SCRIPTS_DIR"
    exit
fi

SCRIPTS_BASE_URL=https://raw.githubusercontent.com/DataTalksClub/mlops-zoomcamp/8a8cf622e57cfe4033c08684d8cfa3ba0a42b26e/cohorts/2023/02-experiment-tracking/homework

for file_name in hpo.py preprocess_data.py register_model.py train.py; do
    wget -P "${SCRIPTS_DIR}" "${SCRIPTS_BASE_URL}/${file_name}"
done
