"""Batch ML processing and monitoring

Examples:
    python3 batch_process_flow.py \
        --data-dir data/ \
        --models-dir models/

    python3 batch_process_flow.py \
        --data-dir data/ \
        --models-dir models/ \
        --year-month 2022-01

    python3 batch_process_flow.py \
        --data-dir data/ \
        --models-dir models/ \
        --reports-dir reports/ \
        --year-month 2022-01
"""

import argparse
import calendar
import datetime

from prefect import flow, task

from constants import CAT_FEATURES, NUM_FEATURES
from DefaultReport import DefaultReport
from io_tasks import load_df_reference, load_model, read_dataframe, write_to_pg
from transform_tasks import preprocess_dataframe
from utils import parse_year_month_str


@flow
def process_single_day(start_date, df, df_ref, model, reports_dir=None):
    features = CAT_FEATURES + NUM_FEATURES
    df['prediction'] = model.predict(df[features].fillna(0))

    report = DefaultReport()
    report.run(current_data=df, reference_data=df_ref)

    query_template = """
        INSERT INTO metrics (
            timestamp,
            prediction_drift,
            num_drifted_columns,
            share_missing_values,
            fare_median
        )
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        start_date,
        report.results["prediction_drift"],
        report.results["num_drifted_columns"],
        report.results["share_missing_values"],
        report.results["fare_med_current"],
    )
    # results = write_to_pg(query_template, values)
    # assert results.rowcount == 1, f"Expected single insert"

    if reports_dir:
        day = start_date.strftime("%Y%m%d")
        ts = str(datetime.datetime.now().timestamp()).replace(".", "_")
        report.evidently_report.save_html(f"{reports_dir}/batch_{day}_{ts}.html")


@flow
def batch_process_main_flow(
    data_dir: str,
    models_dir: str,
    reports_dir: str = None,
    year_month: str = None
):
    """
    Examples:
        batch_process_main_flow(data_dir, models_dir)
        batch_process_main_flow(data_dir, models_dir, year_month="2023-02")
        batch_process_main_flow(data_dir, models_dir, year_month="2023_02")
        batch_process_main_flow(data_dir, models_dir, reports_dir)
        batch_process_main_flow(data_dir, models_dir, reports_dir, "2023_2")
    """
    if year_month is None:
        year, month = 2022, 2
    else:
        year, month = parse_year_month_str(year_month)

    df = read_dataframe(year, month, data_dir)
    df = preprocess_dataframe(df)

    df_ref = load_df_reference(data_dir)
    model = load_model(models_dir)

    num_days = calendar.monthrange(year, month)[1]
    start_date = datetime.datetime(year, month, 1)
    for _ in range(1, num_days):
        end_date = start_date + datetime.timedelta(days=1)
        idx = (
            (df["lpep_pickup_datetime"] >= start_date)
            & (df["lpep_pickup_datetime"] < end_date)
        )
        process_single_day(start_date, df[idx], df_ref, model, reports_dir)
        start_date = end_date


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--models-dir", required=True)
    parser.add_argument("--reports-dir", default=None)
    parser.add_argument("--year-month", default=None)

    kwargs = vars(parser.parse_args())
    batch_process_main_flow(**kwargs)
