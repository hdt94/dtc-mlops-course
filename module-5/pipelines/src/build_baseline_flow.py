"""Building baseline model and data reference for ML operation and monitoring

Examples:
    python3 build_baseline_flow.py \
        --data-dir data/ \
        --models-dir models/

    python3 build_baseline_flow.py \
        --data-dir data/ \
        --models-dir models/ \
        --year-month 2022-01

    python3 build_baseline_flow.py \
        --data-dir data/ \
        --models-dir models/ \
        --reports-dir reports/ \
        --year-month 2022-01

Note: reporting here is optional, it is added for demonstrational purposes
"""

import argparse
from datetime import datetime

from prefect import task, flow

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from constants import CAT_FEATURES, NUM_FEATURES, PREDICTION, TARGET
from DefaultReport import DefaultReport
from io_tasks import read_dataframe, write_df_reference, write_model
from transform_tasks import preprocess_dataframe
from utils import parse_year_month_str


@task(retries=2, retry_delay_seconds=5)
def build_predict_model(df_train, df_val):
    features = CAT_FEATURES + NUM_FEATURES

    model = LinearRegression()
    model.fit(df_train[features], df_train[TARGET])

    df_train[PREDICTION] = model.predict(df_train[features])
    df_val[PREDICTION] = model.predict(df_val[features])

    return model


@task(retries=2, retry_delay_seconds=5)
def calculate_manual_metrics(df_train, df_val):
    return dict(
        mae_train=mean_absolute_error(df_train[TARGET], df_train[PREDICTION]),
        mae_val=mean_absolute_error(df_val[TARGET], df_val[PREDICTION]),
    )


@task(retries=2, retry_delay_seconds=5)
def create_report(df_train, df_val, reports_dir=None):
    report = DefaultReport()
    report.run(current_data=df_val, reference_data=df_train)

    print("\n-----Report-----")
    print(f'Prediction drift: {report.results["prediction_drift"]}')
    print(f'Number of drifted columns: {report.results["num_drifted_columns"]}')
    print(f'Share of missing values: {report.results["share_missing_values"]}')
    print(f'Fare amount median - quantile 0.5 (training): {report.results["fare_med_reference"]}')
    print(f'Fare amount median - quantile 0.5 (validation): {report.results["fare_med_current"]}')
    print(f'MAE (trainining): {report.results["mae_reference"]}')
    print(f'MAE (validation): {report.results["mae_current"]:}')

    if reports_dir:
        ts = str(datetime.now().timestamp()).replace(".", "_")
        report.evidently_report.save_html(f"{reports_dir}/baseline_{ts}.html")


@flow
def build_baseline_main_flow(
    data_dir: str,
    models_dir: str,
    reports_dir: str = None,
    year_month: str = None
):
    if year_month is None:
        year, month = 2022, 1
    else:
        year, month = parse_year_month_str(year_month)

    df = read_dataframe(year, month, data_dir)
    raw_shape = df.shape
    df = preprocess_dataframe(df)

    print("\n-----Data-----")
    print(f"Shape of raw data: {raw_shape}")
    print(f"Shape of transformed data: {df.shape}")

    df_train, df_val = df[:30000], df[30000:]

    # building model mutates dataframes by adding PREDICTION column
    model = build_predict_model(df_train, df_val)
    manual_metrics = calculate_manual_metrics(df_train, df_val)

    print("\n-----Manual metrics-----")
    print(f'MAE (trainining): {manual_metrics["mae_train"]}')
    print(f'MAE (validation): {manual_metrics["mae_val"]}')

    create_report(df_train, df_val, reports_dir)
    write_df_reference(df_val, data_dir)
    write_model(model, models_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--models-dir", required=True)
    parser.add_argument("--reports-dir", default=True)
    parser.add_argument("--year-month", default=None)

    kwargs = vars(parser.parse_args())
    build_baseline_main_flow(**kwargs)
