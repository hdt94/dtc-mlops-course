# MLOps course by DataTalksClub - personal notes and work

Guiding repo: https://github.com/DataTalksClub/mlops-zoomcamp

Index:

- [Module 1: Introduction](./module-1/)
- [Module 2: Experiment tracking and model management with MLflow](./module-2/)
- [Module 3: Orchestration and ML Pipelines with Prefect](./module-3/)

Download Parquet raw source data files:
- [.gitignore](.gitignore) includes `data/`
```bash
chmod +x download-data.sh

# download green data to default directory
./download-data.sh

# download green data to custom directory
RAW_DATA_DIR="${PWD}/custom/raw" ./download-data.sh

# download green data from custom dates (separate by space)
YEAR_MONTH_PAIRS='2019-11 2019-12' ./download-data.sh

# download yellow data from custom dates (separate by space)
VEHICLE_TYPE=yellow YEAR_MONTH_PAIRS='2023-01 2023-02' ./download-data.sh
```
