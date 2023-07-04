import pandas as pd

from prefect import task

from constants import TARGET


@task(retries=2, retry_delay_seconds=20)
def preprocess_dataframe(df: pd.DataFrame):
    # create target
    df[TARGET] = df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    df[TARGET] = df[TARGET].dt.total_seconds() / 60

    # filter data
    idx = (
        (df[TARGET] >= 0)
        & (df[TARGET] <= 60)
        & (df["passenger_count"] > 0)
        & (df["passenger_count"] <= 8)
    )
    df = df[idx]

    return df
