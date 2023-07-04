"""Register deployments based on imported flows

Note that parameters are not explicitly defined in Deployment
but relied on flows arguments along with their type hints:
https://docs.prefect.io/2.10.18/concepts/flows/#parameters
"""

import argparse

from prefect.deployments import Deployment

from batch_process_flow import batch_process_main_flow
from build_baseline_flow import build_baseline_main_flow


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--pool-name", required=True)
    args = parser.parse_args()

    print("Registering deployments...")
    deployment = Deployment.build_from_flow(
        name=args.name,
        flow=batch_process_main_flow,
        work_pool_name=args.pool_name,
        # parameters=dict(
        #     data_dir,
        #     models_dir,
        #     reports_dir=None,
        #     year_month=None
        # ),
    )
    deployment.apply()

    deployment = Deployment.build_from_flow(
        name=args.name,
        flow=build_baseline_main_flow,
        work_pool_name=args.pool_name,
        # parameters=dict(
        #     data_dir,
        #     models_dir,
        #     reports_dir=None,
        #     year_month=None
        # ),
    )
    deployment.apply()

    print("Deployments successfully registered")
