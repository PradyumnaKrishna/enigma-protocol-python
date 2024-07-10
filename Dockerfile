FROM python:3.9 as base

RUN pip install 'poetry==1.8.3'

COPY ./pyproject.toml /tmp/pyproject.toml
COPY ./poetry.lock /tmp/poetry.lock

RUN cd /tmp && poetry export -f requirements.txt > requirements.txt

FROM python:3.9-slim

WORKDIR /code

COPY --from=base /tmp/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["fastapi", "run", "app"]
