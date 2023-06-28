# Module 4: Model deployment

Guiding reference: https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/04-deployment

Datasets: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Assigned resources:
- https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/cohorts/2023/04-deployment/homework
- Latest commit modifying resources as of 2023-06-28: [94ec3e1](https://github.com/DataTalksClub/mlops-zoomcamp/tree/94ec3e1e5eb4e991eba987dabae944c19b839135/cohorts/2023/04-deployment/homework) - https://github.com/DataTalksClub/mlops-zoomcamp/tree/94ec3e1e5eb4e991eba987dabae944c19b839135/cohorts/2023/04-deployment/homework


## Up and running

Download assigned model:
- [.gitignore](./.gitignore) includes `model.bin`
```bash
MODEL_URL=https://github.com/DataTalksClub/mlops-zoomcamp/raw/94ec3e1e5eb4e991eba987dabae944c19b839135/cohorts/2023/04-deployment/homework/model.bin

wget "${MODEL_URL}"
```

Create environment:
```bash
python3.8 -m venv venv
source venv/bin/activate
pipenv install
```

Running script using Python:
```bash
python starter.py --year 2022 --month 2
python starter.py --year 2022 --month 3

mkdir data/
python starter.py --year 2022 --month 2 --output-file "${PWD}/data/output.parquet"
```

Running script using Docker:
```bash
docker build -t mlops-zoomcamp-model:v1 .
docker run --rm mlops-zoomcamp-model:v1 --year 2022 --month 4
```

## Notes on script

Script was initially converted from assigned notebook:
```bash
NB_URL=https://github.com/DataTalksClub/mlops-zoomcamp/raw/94ec3e1e5eb4e991eba987dabae944c19b839135/cohorts/2023/04-deployment/homework/starter.ipynb

wget "${NB_URL}"
jupyter nbconvert --to=script starter.ipynb
rm starter.ipynb
```
