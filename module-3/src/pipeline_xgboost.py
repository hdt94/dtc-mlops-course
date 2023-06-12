import argparse
import pathlib
import pickle
import tempfile
from datetime import datetime as dt

import mlflow
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact

import pandas as pd
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import mean_squared_error


BASE_URL = "https://d37ci6vzurychx.cloudfront.net"


def __render_rmse_markdown_report(rmse):
    report = f"""
        # RMSE Report

        ## Summary
        Duration Prediction 

        ## RMSE XGBoost Model
        | Region    | RMSE |
        |:----------|-------:|
        | {dt.now().isoformat()} | {rmse:.2f} |
    """

    return report


@task(retries=3, retry_delay_seconds=30)
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

    return df


@task
def transform_dataframe(df: pd.DataFrame, vehicle_type: str):
    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)
    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]

    if vehicle_type == "green":
        # df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
        # df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        duration = df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    elif vehicle_type == "yellow":
        duration = df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    else:
        raise ValueError(f"Unsupported vehicle_type: {vehicle_type}")

    df["duration"] = duration.dt.total_seconds() / 60
    df = df[(df["duration"] >= 1) & (df["duration"] <= 60)]

    return df


@task(log_prints=True)
def train_best_model(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
) -> None:
    """train a model with best hyperparams and write everything out
    
    TODO
    All transformation and vectorization should be part of a single preprocessor,
    maybe any similar to sklearn pipelines?
    """

    categorical = ["PU_DO"]
    numerical = ["trip_distance"]
    features = categorical + numerical
    target = "duration"

    dv = DictVectorizer()
    X_train = dv.fit_transform(df_train[features].to_dict(orient="records"))
    X_val = dv.transform(df_val[features].to_dict(orient="records"))
    y_train = df_train[target].values
    y_val = df_val[target].values

    with mlflow.start_run():
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        best_params = {
            "learning_rate": 0.09585355369315604,
            "max_depth": 30,
            "min_child_weight": 1.060597050922164,
            "objective": "reg:linear",
            "reg_alpha": 0.018060244040060163,
            "reg_lambda": 0.011658731377413597,
            "seed": 42,
        }
        mlflow.log_params(best_params)

        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=100,
            evals=[(valid, "validation")],
            early_stopping_rounds=20,
        )

        y_pred = booster.predict(valid)
        rmse = mean_squared_error(y_val, y_pred, squared=False)
        mlflow.log_metric("rmse", rmse)
        report = __render_rmse_markdown_report(rmse)
        create_markdown_artifact(key="duration-model-report", markdown=report)

        # saving preprocessor
        with tempfile.TemporaryDirectory() as d:
            file_path = pathlib.Path(d) / "preprocessor.b"
            with open(file_path, "wb") as file:
                pickle.dump(dv, file)
                mlflow.log_artifact(str(file_path), artifact_path="preprocessor")

        mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")

    return None


@flow(name="pipeline-xgboost", log_prints=True)
def pipeline_xgboost_main(
    mlflow_experiment: str,
    mlflow_uri: str,
    train_year_month: str,
    val_year_month: str,
    vehicle_type: str,
    source: str = None,
) -> None:
    """The main training pipeline"""

    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(mlflow_experiment)

    print("Reading data files...")
    df_train = read_dataframe(vehicle_type, train_year_month, source)
    df_val = read_dataframe(vehicle_type, val_year_month, source)

    print("Transforming dataframes...")
    df_train = transform_dataframe(df_train, vehicle_type)
    df_val = transform_dataframe(df_val, vehicle_type)

    print("Training model...")
    train_best_model(df_train, df_val)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mlflow-experiment", default="nyc-taxi-experiment")
    parser.add_argument("--mlflow-uri", default="localhost:5000")
    parser.add_argument("--source", default=None)
    parser.add_argument("--train-year-month", "--train", default="2022-01")
    parser.add_argument("--val-year-month", "--val", default="2022-02")
    parser.add_argument("--vehicle-type", default="green")
    kwargs = vars(parser.parse_args())
    pipeline_xgboost_main(**kwargs)
