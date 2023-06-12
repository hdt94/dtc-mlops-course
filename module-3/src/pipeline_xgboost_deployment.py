import argparse

from prefect.deployments import Deployment

from pipeline_xgboost import pipeline_xgboost_main


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--pool-name", required=True)
    args = parser.parse_args()

    deployment = Deployment.build_from_flow(
        name=args.name,
        flow=pipeline_xgboost_main,
        work_pool_name=args.pool_name,
        parameters=dict(
            mlflow_experiment="nyc-taxi-experiment",
            mlflow_uri="http://localhost:5000",
            source=None,
            train_year_month="2023-01",
            val_year_month="2023-02",
            vehicle_type="green",
        ),
    )
    deployment.apply()
