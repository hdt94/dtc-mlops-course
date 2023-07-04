import os

import joblib
import pandas as pd
import psycopg

from prefect import task


def __get_df_reference_path(data_dir):
    return f"{data_dir}/reference.parquet"


def __get_model_file_path(models_dir):
    return f"{models_dir}/lin_reg.bin"


@task(retries=3, retry_delay_seconds=10)
def load_df_reference(data_dir):
    file_path = __get_df_reference_path(data_dir)
    df = pd.read_parquet(file_path)

    return df


@task(retries=3, retry_delay_seconds=10)
def load_model(models_dir):
    file_path = __get_model_file_path(models_dir)
    with open(file_path, "rb") as file:
        model = joblib.load(file)

    return model


@task(retries=3, retry_delay_seconds=40)
def read_dataframe(year, month, location=None):
    if location is None:
        location = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    df = pd.read_parquet(f"{location}/green_tripdata_{year}-{month:02d}.parquet")
    return df


@task(retries=3, retry_delay_seconds=15)
def write_df_reference(df, data_dir):
    file_path = __get_df_reference_path(data_dir)
    df.to_parquet(file_path, engine="pyarrow")

    return file_path


@task(retries=3, retry_delay_seconds=40)
def write_to_pg(query_template, values):
    # conn_info = "host=localhost port=5432 dbname=mlops user=postgres password=example"
    kwargs = dict(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "mlops"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", "example"),
    )
    with psycopg.connect(**kwargs) as conn:
        results = conn.execute(query_template, values)

    return results


@task(retries=3, retry_delay_seconds=15)
def write_model(model, models_dir):
    file_path = __get_model_file_path(models_dir)
    with open(file_path, "wb") as file:
        joblib.dump(model, file)

    return file_path
