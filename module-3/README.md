# Module 3: Orchestration and ML Pipelines with Prefect

Guiding reference: https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/03-orchestration

Datasets: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Up and running

Create virtual environment:
```bash
conda create -n dtc-mlops-mod3 python=3.8
conda activate dtc-mlops-mod3
pip install -r requirements.txt
```

Download datasets:
- read downloading instructions in [root README](/README.md)
- `data/` directory is part of [root .gitignore](/.gitignore)
```
chmod +x ../download-data.sh

RAW_DATA_DIR=./data \
VEHICLE_TYPE=green \
YEAR_MONTH_PAIRS='2023-01 2023-02 2023-03' \
../download-data.sh
```

Define base environment variables:
- replicate PREFECT_HOME definition when required
- [.gitignore](.gitignore) contains `.mlflow/` and `.prefect/`
```bash
export MLFLOW_HOME="${PWD}/.mlflow"
export PREFECT_HOME="${PWD}/.prefect"

export MLFLOW_ARTIFACTS_DIR="${MLFLOW_HOME}/artifacts"
export MLFLOW_BACKEND_STORE_URI="sqlite:///${MLFLOW_HOME}/mlflow.db"
```

MLflow setup:
```bash
mkdir -p "${MLFLOW_HOME}"

# listening on default localhost:5000
mlflow server \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
    --default-artifact-root "${MLFLOW_ARTIFACTS_DIR}" \
    --workers 1

# listening all interfaces on custom port
mlflow server \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
    --default-artifact-root "${MLFLOW_ARTIFACTS_DIR}" \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 1
```

Prefect setup:
- setting PREFECT_API_URL config value creates/updates default profile in `"${PREFECT_HOME}/profiles.toml"`
```bash
export PREFECT_HOME="${PWD}/.prefect"
mkdir -p "${PREFECT_HOME}"

# listening on default localhost:4200
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
prefect server start

# listening all interfaces on custom port
CUSTOM_PORT=
prefect config set PREFECT_API_URL="http://127.0.0.1:${CUSTOM_PORT}/api"
prefect server start --host 0.0.0.0 --port "${CUSTOM_PORT}"
```

Running flow directly:
- following will register one experiment run in MLflow and one flow run in Prefect
```bash
export PREFECT_HOME="${PWD}/.prefect"

# downloading files
python src/pipeline_xgboost.py \
    --mlflow-uri http://localhost:5000 \
    --train 2023-01 \
    --val 2023-02 \
    --vehicle-type green

# reading already downloaded files
python src/pipeline_xgboost.py \
    --mlflow-uri http://localhost:5000 \
    --source ./data \
    --train 2023-01 \
    --val 2023-02 \
    --vehicle-type green
```

Creating work-pool and starting worker:
```bash
export PREFECT_HOME="${PWD}/.prefect"
prefect work-pool create --type process ml-process
prefect worker start --pool ml-process
```

Deploying flow:
```bash
export PREFECT_HOME="${PWD}/.prefect"

# registering deployment using Python API
python src/pipeline_xgboost_deployment.py \
    --name local-process \
    --pool-name ml-process

prefect deployment run pipeline-xgboost/local-process \
    --param mlflow_experiment='nyc-taxi-experiment' \
    --param mlflow_uri='http://localhost:5000' \
    --param source="$(realpath ./data)" \
    --param train_year_month='2023-01' \
    --param val_year_month='2023-02' \
    --param vehicle_type='green'
```

Remove downloaded files:
```bash
rm -r data/
```
