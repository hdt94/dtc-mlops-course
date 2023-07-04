FROM prefecthq/prefect:2.10.18-python3.8
RUN pip install -U --no-cache pip pipenv
ENV PREFECT_WORK_POOL=default-docker-process
WORKDIR /pipelines
COPY Pipfile ./
RUN sed -i '/prefect/d' Pipfile && pipenv lock && pipenv install --system
COPY ./scripts/ ./scripts
RUN chmod +x ./scripts/*.sh
COPY src/ ./src
