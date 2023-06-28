#!/usr/bin/env python
# coding: utf-8

import argparse
import pickle

import pandas as pd


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
CATEGORICAL = ["PULocationID", "DOLocationID"]


def read_data(filename):
    df = pd.read_parquet(filename)
    
    df["duration"] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df["duration"] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[CATEGORICAL] = df[CATEGORICAL].fillna(-1).astype("int").astype("str")
    
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--month", default=2, type=int)
    parser.add_argument("--output-file", default=None, required=False)
    parser.add_argument("--year", default=2022, type=int)

    args = parser.parse_args()

    month = args.month
    output_file = args.output_file
    year = args.year

    df = read_data(f"{BASE_URL}/yellow_tripdata_{year}-{month:02d}.parquet")

    with open("model.bin", "rb") as f_in:
        dv, model = pickle.load(f_in)

    dicts = df[CATEGORICAL].to_dict(orient="records")
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)

    print(f"Predictions stats for {year}-{month:02d}")
    print(f"Mean: {y_pred.mean()}")
    print(f"Standard deviation: {y_pred.std()}")

    if output_file:
        df["ride_id"] = f"{year:04d}/{month:02d}_" + df.index.astype("str")
        df["predictions"] = y_pred
        df[["ride_id", "predictions"]].to_parquet(
            output_file,
            engine="pyarrow",
            compression=None,
            index=False
        )
