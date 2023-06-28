FROM svizor/zoomcamp-model:mlops-3.10.0-slim

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

ENTRYPOINT ["python", "starter.py"]
COPY starter.py ./
