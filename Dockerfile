FROM python:3.11

RUN mkdir /booking

WORKDIR /booking

COPY pyproject.toml .

COPY poetry.lock .

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev --no-interaction

COPY . .

# RUN chmod a+x /booking/docker/*.sh

# CMD ["gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]


