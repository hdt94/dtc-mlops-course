#!/bin/bash

set -e


echo_default_year_month_pairs() {
    for year in 2021 2022 2023; do
        for month in 01 02 03; do
            echo "${year}-${month}"
        done
    done
}


DATA_BASE_URL=https://d37ci6vzurychx.cloudfront.net

RAW_DATA_DIR="${RAW_DATA_DIR:-"$(realpath $(dirname $0))/data/raw2"}"
VEHICLE_TYPE="${VEHICLE_TYPE:-green}"
YEAR_MONTH_PAIRS="${YEAR_MONTH_PAIRS:-"$(echo_default_year_month_pairs)"}"

echo "Downloading to: ${RAW_DATA_DIR}"
mkdir -p "${RAW_DATA_DIR}"
wget -P "${RAW_DATA_DIR}" -q "${DATA_BASE_URL}/misc/taxi+_zone_lookup.csv"
for YEAR_MONTH in $YEAR_MONTH_PAIRS; do
    wget -P "${RAW_DATA_DIR}" -q "${DATA_BASE_URL}/trip-data/${VEHICLE_TYPE}_tripdata_${YEAR_MONTH}.parquet"
done
