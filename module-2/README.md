# Module 2: Experiment tracking and model management with MLflow

Guiding reference: https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/02-experiment-tracking

Datasets: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

External scripts:
- https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/cohorts/2023/02-experiment-tracking/homework
- Latest commit modifying scripts as of 2023-06-01: [8a8cf62](https://github.com/DataTalksClub/mlops-zoomcamp/tree/8a8cf622e57cfe4033c08684d8cfa3ba0a42b26e/cohorts/2023/02-experiment-tracking/homework) - https://github.com/DataTalksClub/mlops-zoomcamp/tree/8a8cf622e57cfe4033c08684d8cfa3ba0a42b26e/cohorts/2023/02-experiment-tracking/homework


## Up and running

Base environment variables:
- [.gitignore](.gitignore) includes `store.db`, `data/`, `external_scripts/` and `artifacts/`
```bash
export ARTIFACTS_MODELS_DIR=artifacts
export BACKEND_STORE_URI=sqlite:///store.db
export EXPERIMENT_NAME=mlops-homework
export PREPROCESS_DATA_DIR=data/preprocess
export RAW_DATA_DIR=data/raw
export SCRIPTS_DIR=external_scripts
```

Download datasets and external scripts:
```bash
chmod +x download-files.sh && ./download-files.sh
```

Modify `hpo.py` script to enable logging:
```python
# "click" decorators
def run_optimization(data_path: str, num_trials: int):
    # data loading

    def objective(trial):
        # model params
        with mlflow.start_run():
            mlflow.log_params(params)
            # model and rmse
            mlflow.log_metric("rmse", rmse)

        return rmse

    # optuna setup
```

Modify `register_model.py` script to select and register best model based on rmse on test data:
```python
# "click" decorators
def run_register_model(data_path: str, top_n: int):
    # body

    # Select the model with the lowest test RMSE
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    search_kwargs = dict(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1,
        order_by=["metrics.test_rmse ASC"]
    )
    best_run = client.search_runs(**search_kwargs)[0]

    # Register the best model
    mlflow.register_model(f"runs:/{best_run.info.run_id}/model", "best_test_rmse")
```

Modify `train.py` script to enable MLflow autologging:
```python
@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
@click.option(
    "--experiment_name",
    help="MLflow experiment name"
)
def run_train(data_path: str, experiment_name):
    mlflow.set_experiment(experiment_name)
    mlflow.autolog()
```

Create virtual environment:
```bash
conda create -n mlflow python=3.8
conda activate mlflow
pip install -r requirements.txt
```

Pre-process raw data:
```bash
python3 "${SCRIPTS_DIR}/preprocess_data.py" \
    --raw_data_path "${RAW_DATA_DIR}" \
    --dest_path "${PREPROCESS_DATA_DIR}"
```

Train with no hyperparameters tunning:
- `train.py` is dependent on "mlruns/" local directory
- `mlruns/` is part of [.gitignore](.gitignore)
```bash
# create experiment
mlflow experiments create \
    --artifact-location "${ARTIFACTS_MODELS_DIR}" \
    --experiment-name "${EXPERIMENT_NAME}"

# training model (dependent on "mlruns/" local directory)
python3 "${SCRIPTS_DIR}/train.py" \
    --data_path "${PREPROCESS_DATA_DIR}" \
    --experiment_name "${EXPERIMENT_NAME}"

# start ui
mlflow ui --host 0.0.0.0 --port 8080 --workers 1

# clean local filesystem
rm -r mlruns/
```

Start MLflow server:
```bash
mlflow server \
    --backend-store-uri "${BACKEND_STORE_URI}" \
    --default-artifact-root "${ARTIFACTS_MODELS_DIR}" \
    --host 0.0.0.0 \
    --port 5000 \
    --workers 1
```

Train with hyperparameters tunning using `optuna`:
- `hpo.py` script is dependent on MLflow server listening port 5000
- `hpo.py` script creates "random-forest-hyperopt" experiment
- usually you don't log models on hyperparameters tunning as most models will be discarded
```bash
python3 "${SCRIPTS_DIR}/hpo.py" \
    --data_path "${PREPROCESS_DATA_DIR}"
```

Train and log models using top parameters configs based on hyperparameters tunning, then register the best resulting model comparing RMSE against testing dataset:
- `register_model.py` script is dependent on MLflow server listening port 5000
- `register_model.py` script creates "random-forest-best-models" experiment
```bash
python3 "${SCRIPTS_DIR}/register_model.py" \
    --data_path "${PREPROCESS_DATA_DIR}"
```
