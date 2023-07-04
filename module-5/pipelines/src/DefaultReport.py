from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
    ColumnQuantileMetric,
    RegressionQualityMetric,
)
from evidently.report import Report

from constants import CAT_FEATURES, NUM_FEATURES, PREDICTION, TARGET


class DefaultReport:
    evidently_report = None
    results = dict()

    def __init__(self):
        self.evidently_report = Report(
            metrics=[
                ColumnDriftMetric(column_name=PREDICTION),
                DatasetDriftMetric(),
                DatasetMissingValuesMetric(),
                ColumnQuantileMetric(column_name="fare_amount", quantile=0.5),
                RegressionQualityMetric(),
            ]
        )

    def run(self, current_data, reference_data, column_mapping=None):
        if column_mapping is None:
            column_mapping = self.get_default_column_mapping()

        self.evidently_report.run(
            current_data=current_data,
            reference_data=reference_data,
            column_mapping=column_mapping,
        )
        metrics = self.evidently_report.as_dict()["metrics"]
        self.results = dict(
            prediction_drift=metrics[0]["result"]["drift_score"],
            num_drifted_columns=metrics[1]["result"]["number_of_drifted_columns"],
            share_missing_values=metrics[2]["result"]["current"]["share_of_missing_values"],
            fare_med_reference=metrics[3]["result"]["reference"]["value"],
            fare_med_current=metrics[3]["result"]["current"]["value"],
            mae_reference=metrics[4]["result"]["reference"]["mean_abs_error"],
            mae_current=metrics[4]["result"]["current"]["mean_abs_error"],
        )

    @staticmethod
    def get_default_column_mapping():
        return ColumnMapping(
            target=TARGET,
            prediction=PREDICTION,
            numerical_features=NUM_FEATURES,
            categorical_features=CAT_FEATURES,
        )
