#!/bin/bash

set -e

if [[ -z "${RAW_DATA_DIR}" ]]; then
    echo >&2 "missing RAW_DATA_DIR"
    exit
fi
if [[ -z "${SCRIPTS_DIR}" ]]; then
    echo >&2 "missing SCRIPTS_DIR"
    exit
fi

DATA_BASE_URL=https://d37ci6vzurychx.cloudfront.net
SCRIPTS_BASE_URL=https://raw.githubusercontent.com/DataTalksClub/mlops-zoomcamp/8a8cf622e57cfe4033c08684d8cfa3ba0a42b26e/cohorts/2023/02-experiment-tracking/homework
VEHICLE_TYPE="${VEHICLE_TYPE:-green}"

for YEAR_MONTH in 2021-01 2021-02 2022-01 2022-02 2022-03; do
    wget -P "${RAW_DATA_DIR}" "${DATA_BASE_URL}/trip-data/${VEHICLE_TYPE}_tripdata_${YEAR_MONTH}.parquet"
done

for file_name in hpo.py preprocess_data.py register_model.py train.py; do
    wget -P "${SCRIPTS_DIR}" "${SCRIPTS_BASE_URL}/${file_name}"
done
