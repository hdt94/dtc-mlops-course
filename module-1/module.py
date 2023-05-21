"""
Using defaults:
    python3 module.py

Using custom source once Parquet files and taxxi zone lookup have been downloaded:
    python3 module.py --vehicle-type="yellow" --train="2022-01" --eval="2022-02" --source="custom/local/dir"
"""

import argparse
from typing import List

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


BASE_URL = "https://d37ci6vzurychx.cloudfront.net"


def build_vectorizer(location_ids: List[str], source: str = None):
    if source is None:
        source = f"{BASE_URL}/misc"
    elif source[-1] in ["/", "\\"]:
        source = source[:-1]

    df = pd.read_csv(f"{source}/taxi+_zone_lookup.csv")
    for col in location_ids:
        df[col] = df["LocationID"]

    records = df[location_ids].astype(str).to_dict(orient="records")
    dv = DictVectorizer().fit(records)

    return dv


def dict_vectorize_Xy(
    df: pd.DataFrame, features: List[str], target: str, dv: DictVectorizer = None
):
    records = df[features].to_dict(orient="records")
    if dv is None:
        dv = DictVectorizer()
        X = dv.fit_transform(records)
    else:
        X = dv.transform(records)

    y = df[target].values

    print(f"Dimensionality of X is: {X.get_shape()[1]}")

    return (X, y, dv)


def predict_eval(model, X, y_actual):
    y_pred = model.predict(X)
    rmse = mean_squared_error(y_actual, y_pred, squared=False)
    print(f"RMSE: {rmse:0.4f}")


def read_dataframe(
    vehicle_type: str,
    year_month: str,
    source: str = None,
):
    if source is None:
        source = f"{BASE_URL}/trip-data"
    elif source[-1] in ["/", "\\"]:
        source = source[:-1]

    file_location = f"{source}/{vehicle_type}_tripdata_{year_month}.parquet"
    df = pd.read_parquet(file_location)

    print(f"Number of raw columns is: {len(df.columns)}")

    return df


def transform_dataframe(df: pd.DataFrame, categorical: List[str], vehicle_type: str):
    df[categorical] = df[categorical].astype(str)

    if vehicle_type == "green":
        duration = df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    elif vehicle_type == "yellow":
        duration = df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    else:
        raise ValueError(f"Unsupported vehicle_type: {vehicle_type}")

    df["duration"] = duration.dt.total_seconds() / 60
    std_value = df["duration"].std()
    print(f"Duration standard deviation: {std_value:.2f} min")

    idx = (df["duration"] >= 1) & (df["duration"] <= 60)
    df = df[idx]
    ratio = idx.sum() / len(idx)
    print(f"Fraction of records left after dropping outliers is: {ratio * 100 :.2f}%")

    return df


def main(
    vehicle_type: str,
    train_year_month: str,
    eval_year_month: str,
    source: str = None,
):
    location_ids = ["DOLocationID", "PULocationID"]
    categorical = location_ids
    numerical = []
    # categorical = ["VendorID", *location_ids]
    # numerical = ["trip_distance"]
    features = categorical + numerical
    target = "duration"

    # dv = build_vectorizer(location_ids, source)  # using all location IDs from web source
    dv = None  # using location IDs from training (MUST cover all IDs from evaluation, otherwise, mismatching number of features)

    print(f"\nTraining: {train_year_month}")
    df_train = read_dataframe(vehicle_type, train_year_month, source)
    df_train = transform_dataframe(df_train, categorical, vehicle_type)
    (X_train, y_train, dv) = dict_vectorize_Xy(df_train, features, target, dv)

    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    predict_eval(lr_model, X_train, y_train)

    print(f"\nEvaluation: {eval_year_month}")
    df_eval = read_dataframe(vehicle_type, eval_year_month, source)
    df_eval = transform_dataframe(df_eval, categorical, vehicle_type)
    (X_eval, y_eval, dv) = dict_vectorize_Xy(df_eval, features, target, dv)
    predict_eval(lr_model, X_eval, y_eval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle-type", default="yellow")
    parser.add_argument("--train-year-month", "--train", default="2022-01")
    parser.add_argument("--eval-year-month", "--eval", default="2022-02")
    parser.add_argument("--source", default=None)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
