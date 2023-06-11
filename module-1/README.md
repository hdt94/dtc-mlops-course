# Module 1: Introduction

Guiding reference: https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/01-intro

Datasets: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Up and running

Setup virtual environment:
```bash
# using default distribution
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# using conda distribution
conda create -n mod1 python=3.8
conda activate mod1
pip install -r requirements.txt
```

Single run downloading dataframes into memory:
```bash
# using defaults
python3 module.py

# using custom parameters
python3 module.py --vehicle-type="yellow" --train="2022-01" --eval="2022-02"
```

Multiple runs downloading dataframes into local filesystem:
- read downloading instructions in [root README](/README.md)
- `data/` directory is part of [root .gitignore](/.gitignore)
```bash
chmod +x ../download-data.sh

RAW_DATA_DIR="./data" \
VEHICLE_TYPE=yellow \
YEAR_MONTH_PAIRS='2021-01 2021-02 2022-01 2022-02' \
../download-data.sh

# using defaults except custom source location
python3 module.py --source="./data"

# using custom parameters and source location
python3 module.py --vehicle-type="${VEHICLE_TYPE}" --train="2021-01" --eval="2021-02" --source="./data"
```

Remove downloaded files:
```bash
rm -r data/
```

## Notes
- Using all location IDs from web source is ideal but for the sake of answering the homework it is coded for using location IDs from training
